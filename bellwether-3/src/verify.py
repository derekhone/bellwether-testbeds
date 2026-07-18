"""
BELLWETHER-3 — independent verifier.

Recomputes chi per state from the committed raw counts, rebuilds the
contextuality witness, and re-checks the ProofRecord's record_hash and
context_nonce against the raw artifacts. This is the check a skeptical third
party runs: nothing is trusted except the raw counts file and the record.

Usage: python3 src/verify.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import peres_mermin as pm
import contextuality_witness as cw
import proofrecord as pr

RESULTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
RAW = os.path.join(RESULTS, "raw")


def main():
    payload = json.load(open(os.path.join(RAW, "raw_counts.json")))
    meta = json.load(open(os.path.join(RAW, "job_meta.json")))
    cal = json.load(open(os.path.join(RAW, "calibration_snapshot.json")))
    record = json.load(open(os.path.join(RESULTS, "proofrecord.json")))

    shots = meta.get("shots_per_context", 1000)
    states = payload.get("states", meta.get("states", ["00"]))
    counts_by_state = payload["counts_by_state"]

    per_state_results = []
    recomputed = {}
    for state in states:
        chi, E = pm.compute_chi_for_state(counts_by_state[state])
        sigma = pm.shot_noise_sigma_chi(E, shots)
        per_state_results.append(cw.build_state_result(state, chi, E, shots, sigma))
        recomputed[state] = chi
    witness = cw.build_witness(per_state_results, shots)

    rec_witness = record["contextuality_witness"]
    chi_matches = all(
        abs(recomputed[r["state"]] - r["chi"]) < 1e-9
        for r in rec_witness["per_state"]
    )
    checks = {
        "recomputed_chi": recomputed,
        "chi_matches_record": chi_matches,
        "record_hash_valid": pr.verify_record_hash(record),
        "context_nonce_valid": pr.verify_context_nonce(record, payload, cal, witness),
        "violation_all_states": witness["violation_all_states"],
        "significant_all_states_3sigma": witness["significant_all_states_3sigma"],
        "state_independence_demonstrated": witness["state_independence_demonstrated"],
    }
    all_ok = (checks["chi_matches_record"] and checks["record_hash_valid"]
              and checks["context_nonce_valid"])
    print(json.dumps(checks, indent=2))
    print(f"\n[verify] OVERALL: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
