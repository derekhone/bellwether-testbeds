"""
BELLWETHER-1 — QPU submission harness.

Bakes in the hard-won WITNESS lessons so we do not waste the scarce open-plan
budget:
  FIX-1: qiskit-ibm-runtime 0.48.0 `service.least_busy()` can raise TypeError
         -> pick backend via min(pending_jobs) manually.
  FIX-2: IBM rejects non-ISA circuits -> transpile(optimization_level=1) to the
         target backend before submission.
  Channel: ibm_quantum_platform  (not the retired ibm_quantum).
  Mode:    Batch  (open plan forbids Session).

Runs the four CHSH circuits, collects raw counts per setting, snapshots
calibration, computes S + entropy witness, builds the ProofRecord, and writes
all artifacts under results/. Does NOT publish anywhere.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import chsh
import entropy_witness as ew
import proofrecord as pr

SHOTS_PER_SETTING = 1000  # 4 settings x 1000 = 4000 shots total
RESULTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
RAW = os.path.join(RESULTS, "raw")


def _load_token() -> str:
    p = "/home/ubuntu/.config/abacusai_auth_secrets.json"
    d = json.load(open(p))
    return d["witness1_ibmq"]["secrets"]["api_token"]["value"]


def _pick_backend(service, prefer=("ibm_fez", "ibm_marrakesh", "ibm_kingston")):
    """FIX-1: robust least-busy selection via min(pending_jobs)."""
    backends = [b for b in service.backends(operational=True, simulator=False)]
    if not backends:
        raise RuntimeError("no operational hardware backends")
    named = {b.name: b for b in backends}
    for name in prefer:
        if name in named:
            return named[name]
    return min(backends, key=lambda b: b.status().pending_jobs)


def _calibration_snapshot(backend, phys_qubits) -> dict:
    """Deterministic, minimal calibration snapshot for the two used qubits."""
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


def main():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, Batch, SamplerV2

    os.makedirs(RAW, exist_ok=True)
    token = _load_token()
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    backend = _pick_backend(service)
    print(f"[BELLWETHER-1] backend = {backend.name}")

    logical = chsh.build_circuits()
    # FIX-2: transpile to ISA for the target backend.
    isa = transpile(logical, backend=backend, optimization_level=1)

    # Record which physical qubits were used (from the first transpiled circuit).
    try:
        layout = isa[0].layout
        phys = sorted(set(layout.final_index_layout()[:2])) if layout else [0, 1]
    except Exception:
        phys = [0, 1]

    counts_by_setting = []
    job_ids = []
    with Batch(backend=backend) as batch:
        sampler = SamplerV2(mode=batch)
        job = sampler.run(isa, shots=SHOTS_PER_SETTING)
        job_ids.append(job.job_id())
        print(f"[BELLWETHER-1] job_id = {job.job_id()}")
        result = job.result()
        for idx in range(len(isa)):
            # Validated extraction (see PRE-EXECUTION HARNESS FIX in prereg):
            # SamplerV2 DataBin exposes the classical register by name via keys().
            data = result[idx].data
            keys = list(data.keys()) if hasattr(data, "keys") \
                else [k for k in dir(data) if not k.startswith("_")]
            creg = keys[0]
            counts = data[creg].get_counts() if hasattr(data, "__getitem__") \
                else getattr(data, creg).get_counts()
            counts_by_setting.append(counts)
            print(f"  setting {idx}: {counts}")

    S, E = chsh.compute_S(counts_by_setting)
    sigma = chsh.shot_noise_sigma_S(SHOTS_PER_SETTING)
    witness = ew.build_witness(S, E, SHOTS_PER_SETTING, sigma)
    print(f"[BELLWETHER-1] S = {S:.4f}  (classical<=2, Tsirelson={chsh.TSIRELSON_BOUND:.4f})")
    print(f"[BELLWETHER-1] violation={witness['violation']} "
          f"3sigma={witness['significant_violation_3sigma']}")

    cal = _calibration_snapshot(backend, phys)
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    instance = getattr(service, "_account", None)
    provider_instance = "open-instance"
    record = pr.build_proofrecord(counts_by_setting, job_ids[0], backend.name,
                                  provider_instance, cal, witness,
                                  "bellwether-1-primary", ts)

    # Write artifacts
    json.dump({"counts_by_setting": counts_by_setting,
               "settings_order": ["(a,b)", "(a,b')", "(a',b)", "(a',b')"]},
              open(os.path.join(RAW, "raw_counts.json"), "w"), indent=2)
    json.dump({"job_id": job_ids[0], "backend": backend.name,
               "shots_per_setting": SHOTS_PER_SETTING, "timestamp_utc": ts},
              open(os.path.join(RAW, "job_meta.json"), "w"), indent=2)
    json.dump(cal, open(os.path.join(RAW, "calibration_snapshot.json"), "w"), indent=2)
    json.dump(record, open(os.path.join(RESULTS, "proofrecord.json"), "w"), indent=2)
    json.dump({"S": S, "E_values": E, "witness": witness},
              open(os.path.join(RESULTS, "BELLWETHER-1-result.json"), "w"), indent=2)
    print("[BELLWETHER-1] artifacts written under results/")


if __name__ == "__main__":
    main()
