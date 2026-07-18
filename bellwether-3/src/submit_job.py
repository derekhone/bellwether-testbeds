"""
BELLWETHER-3 — QPU submission harness (Peres–Mermin state-independent contextuality).

Bakes in all proven harness lessons:
  FIX-1: pick backend via min(pending_jobs) manually (avoid least_busy TypeError).
  FIX-2: transpile(optimization_level=1) to the target backend ISA before run.
  FIX-3: robust token loader tries ["ibm quantum", "witness1_ibmq", "ibm_quantum"].
  Channel: ibm_quantum_platform.  Mode: Batch (open plan forbids Session).

Runs the six Peres–Mermin context circuits for each configured input STATE
(default: 00, ++, bell -> demonstrates state-independence), collects raw counts,
snapshots calibration, computes chi per state + the contextuality witness, builds
the ProofRecord, and writes all artifacts under results/. Does NOT publish
anywhere (IP file-first gate).
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import peres_mermin as pm
import contextuality_witness as cw
import proofrecord as pr

SHOTS = 1000                     # per context per state
STATES = ["00", "++", "bell"]    # state-independence demonstration
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


def _calibration_snapshot(backend) -> dict:
    snap = {"backend": backend.name, "num_qubits": backend.num_qubits}
    try:
        props = backend.properties()
        if props is not None:
            snap["last_update_date"] = str(getattr(props, "last_update_date", ""))
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


def _assemble(counts_flat, index):
    """Regroup a flat list of counts into {state: [six context counts in order]}."""
    by_state = {}
    for (state, cname), counts in zip(index, counts_flat):
        by_state.setdefault(state, {})[cname] = counts
    ordered = {}
    for state in by_state:
        ordered[state] = [by_state[state][n] for n in pm.CONTEXT_NAMES]
    return ordered


def _finalize(counts_flat, index, job_id, backend_name, cal):
    counts_by_state = _assemble(counts_flat, index)
    per_state_results = []
    for state in STATES:
        chi, E = pm.compute_chi_for_state(counts_by_state[state])
        sigma = pm.shot_noise_sigma_chi(E, SHOTS)
        per_state_results.append(cw.build_state_result(state, chi, E, SHOTS, sigma))
        print(f"  |{state}>: chi = {chi:.4f}  E = {[round(e,3) for e in E]}")
    witness = cw.build_witness(per_state_results, SHOTS)
    print(f"[BELLWETHER-3] chi range [{witness['min_chi']:.3f}, {witness['max_chi']:.3f}]"
          f"  all_violate={witness['violation_all_states']}"
          f"  all_3sigma={witness['significant_all_states_3sigma']}")

    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {"counts_by_state": counts_by_state, "states": STATES,
               "context_order": pm.CONTEXT_NAMES}
    record = pr.build_proofrecord(payload, job_id, backend_name, "open-instance",
                                  cal, witness, "bellwether-3-primary", ts)

    os.makedirs(RAW, exist_ok=True)
    json.dump(payload, open(os.path.join(RAW, "raw_counts.json"), "w"), indent=2)
    json.dump({"job_id": job_id, "backend": backend_name, "shots_per_context": SHOTS,
               "states": STATES, "timestamp_utc": ts},
              open(os.path.join(RAW, "job_meta.json"), "w"), indent=2)
    json.dump(cal, open(os.path.join(RAW, "calibration_snapshot.json"), "w"), indent=2)
    json.dump(record, open(os.path.join(RESULTS, "proofrecord.json"), "w"), indent=2)
    json.dump({"witness": witness},
              open(os.path.join(RESULTS, "BELLWETHER-3-result.json"), "w"), indent=2)
    print("[BELLWETHER-3] artifacts written under results/")


def main():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, Batch, SamplerV2

    os.makedirs(RAW, exist_ok=True)
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=load_token())
    backend = _pick_backend(service)
    print(f"[BELLWETHER-3] backend = {backend.name}")

    logical, index = pm.build_all_circuits(STATES)
    isa = transpile(logical, backend=backend, optimization_level=1)

    counts_flat = []
    with Batch(backend=backend) as batch:
        sampler = SamplerV2(mode=batch)
        job = sampler.run(isa, shots=SHOTS)
        print(f"[BELLWETHER-3] job_id = {job.job_id()}")
        result = job.result()
        for i in range(len(isa)):
            counts_flat.append(_extract_counts(result[i]))
        job_id = job.job_id()

    _finalize(counts_flat, index, job_id, backend.name, _calibration_snapshot(backend))


if __name__ == "__main__":
    main()
