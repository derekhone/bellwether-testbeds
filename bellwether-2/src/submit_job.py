"""
BELLWETHER-2 — QPU submission harness (Mermin-3 / 3-qubit GHZ).

Bakes in all proven harness lessons:
  FIX-1: qiskit-ibm-runtime 0.48.0 `service.least_busy()` can raise TypeError
         -> pick backend via min(pending_jobs) manually.
  FIX-2: IBM rejects non-ISA circuits -> transpile(optimization_level=1) to the
         target backend before submission.
  FIX-3: Robust token loader tries ["ibm quantum", "witness1_ibmq", "ibm_quantum"].
  Channel: ibm_quantum_platform  (not the retired ibm_quantum).
  Mode:    Batch  (open plan forbids Session).

Runs the four Mermin-3 circuits (XYY, YXY, YYX, XXX on 3-qubit GHZ), collects
raw counts, snapshots calibration, computes M + multipartite witness, builds
the ProofRecord, and writes all artifacts under results/. Does NOT publish
anywhere (IP gate).
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import mermin
import multipartite_witness as mw
import proofrecord as pr

SHOTS = 2000  # 4 settings x 2000 = 8000 shots; ~a few seconds of QPU time
RESULTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
RAW = os.path.join(RESULTS, "raw")


def load_token() -> str:
    d = json.load(open("/home/ubuntu/.config/abacusai_auth_secrets.json"))
    for key in ("ibm quantum", "witness1_ibmq", "ibm_quantum"):
        if key in d:
            return d[key]["secrets"]["api_token"]["value"]
    raise RuntimeError("no IBM Quantum token key found in secrets")


def _pick_backend(service, prefer=("ibm_fez", "ibm_marrakesh", "ibm_kingston")):
    backends = [b for b in service.backends(operational=True, simulator=False)]
    if not backends:
        raise RuntimeError("no operational hardware backends")
    named = {b.name: b for b in backends}
    for name in prefer:
        if name in named:
            return named[name]
    return min(backends, key=lambda b: b.status().pending_jobs)


def _calibration_snapshot(backend, phys_qubits) -> dict:
    snap = {"backend": backend.name, "num_qubits": backend.num_qubits,
            "physical_qubits": list(phys_qubits)}
    try:
        props = backend.properties()
        if props is not None:
            snap["last_update_date"] = str(getattr(props, "last_update_date", ""))
            snap["qubit_props"] = {}
            for q in phys_qubits:
                try:
                    snap["qubit_props"][str(q)] = {
                        "T1": props.t1(q), "T2": props.t2(q),
                        "readout_error": props.readout_error(q),
                    }
                except Exception:
                    pass
    except Exception as e:
        snap["properties_error"] = repr(e)[:200]
    return snap


def _extract_counts(pub_result):
    data = pub_result.data
    keys = list(data.keys()) if hasattr(data, "keys") \
        else [k for k in dir(data) if not k.startswith("_")]
    creg = keys[0]
    return data[creg].get_counts() if hasattr(data, "__getitem__") \
        else getattr(data, creg).get_counts()


def main():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, Batch, SamplerV2

    os.makedirs(RAW, exist_ok=True)
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=load_token())
    backend = _pick_backend(service)
    print(f"[BELLWETHER-2] backend = {backend.name}")

    logical = mermin.build_circuits()
    isa = transpile(logical, backend=backend, optimization_level=1)
    try:
        layout = isa[0].layout
        phys = sorted(set(layout.final_index_layout()[:3])) if layout else [0, 1, 2]
    except Exception:
        phys = [0, 1, 2]

    counts_by_setting = []
    with Batch(backend=backend) as batch:
        sampler = SamplerV2(mode=batch)
        job = sampler.run(isa, shots=SHOTS)
        print(f"[BELLWETHER-2] job_id = {job.job_id()}")
        result = job.result()
        for idx in range(len(isa)):
            counts = _extract_counts(result[idx])
            counts_by_setting.append(counts)
            print(f"  {mermin.SETTINGS[idx]}: {counts}")
        job_id = job.job_id()

    M, E = mermin.compute_M(counts_by_setting)
    sigma = mermin.shot_noise_sigma_M(E, SHOTS)
    witness = mw.build_witness(M, E, SHOTS, sigma)
    print(f"[BELLWETHER-2] M = {M:.4f}  (classical<=2, quantum_max=4)")
    print(f"[BELLWETHER-2] violation={witness['violation']} 3sigma={witness['significant_violation_3sigma']}")

    cal = _calibration_snapshot(backend, phys)
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record = pr.build_proofrecord(counts_by_setting, job_id, backend.name,
                                  "open-instance", cal, witness,
                                  "bellwether-2-primary", ts)

    json.dump({"counts_by_setting": counts_by_setting,
               "settings_order": mermin.SETTINGS},
              open(os.path.join(RAW, "raw_counts.json"), "w"), indent=2)
    json.dump({"job_id": job_id, "backend": backend.name,
               "shots_per_setting": SHOTS, "timestamp_utc": ts},
              open(os.path.join(RAW, "job_meta.json"), "w"), indent=2)
    json.dump(cal, open(os.path.join(RAW, "calibration_snapshot.json"), "w"), indent=2)
    json.dump(record, open(os.path.join(RESULTS, "proofrecord.json"), "w"), indent=2)
    json.dump({"M": M, "E_values": E, "witness": witness},
              open(os.path.join(RESULTS, "BELLWETHER-2-result.json"), "w"), indent=2)
    print("[BELLWETHER-2] artifacts written under results/")


if __name__ == "__main__":
    main()
