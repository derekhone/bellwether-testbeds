"""
BELLWETHER-2 — independent verifier.

Recomputes M from the committed raw counts, rebuilds the multipartite witness,
and re-checks the ProofRecord's record_hash and mermin_nonce against the raw
artifacts. This is the check a skeptical third party runs: nothing is trusted
except the raw counts file and the record.

Usage: python3 src/verify.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import mermin
import multipartite_witness as mw
import proofrecord as pr

RESULTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
RAW = os.path.join(RESULTS, "raw")


def main():
    raw = json.load(open(os.path.join(RAW, "raw_counts.json")))
    counts = raw["counts_by_setting"]
    meta = json.load(open(os.path.join(RAW, "job_meta.json")))
    cal = json.load(open(os.path.join(RAW, "calibration_snapshot.json")))
    record = json.load(open(os.path.join(RESULTS, "proofrecord.json")))

    shots = meta.get("shots_per_setting", 2000)
    M, E = mermin.compute_M(counts)
    sigma = mermin.shot_noise_sigma_M(E, shots)
    witness = mw.build_witness(M, E, shots, sigma)

    checks = {
        "recomputed_M": M,
        "recomputed_E_values": E,
        "M_matches_record": abs(M - record["multipartite_witness"]["M"]) < 1e-9,
        "record_hash_valid": pr.verify_record_hash(record),
        "mermin_nonce_valid": pr.verify_mermin_nonce(record, counts, cal, witness),
        "violation": witness["violation"],
        "significant_violation_3sigma": witness["significant_violation_3sigma"],
    }
    all_ok = (checks["M_matches_record"] and checks["record_hash_valid"]
              and checks["mermin_nonce_valid"])
    print(json.dumps(checks, indent=2))
    print(f"\n[verify] OVERALL: {'PASS' if all_ok else 'FAIL'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
