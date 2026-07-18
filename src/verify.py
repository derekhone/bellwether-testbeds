"""
BELLWETHER-1 — independent verifier.

Recomputes S, the entropy witness, and the full provenance chain from the raw
artifacts, and re-checks record_hash + bell_nonce. Any independent party can run
this against the committed results/ to reproduce the verdict.

Run: python3 src/verify.py
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import chsh
import entropy_witness as ew
import proofrecord as pr

RESULTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
RAW = os.path.join(RESULTS, "raw")


def main() -> int:
    raw = json.load(open(os.path.join(RAW, "raw_counts.json")))
    counts = raw["counts_by_setting"]
    cal = json.load(open(os.path.join(RAW, "calibration_snapshot.json")))
    record = json.load(open(os.path.join(RESULTS, "proofrecord.json")))

    S, E = chsh.compute_S(counts)
    sigma = chsh.shot_noise_sigma_S(sum(counts[0].values()))
    witness = ew.build_witness(S, E, sum(counts[0].values()), sigma)

    checks = {
        "S_recomputed": round(S, 6),
        "violation": witness["violation"],
        "significant_violation_3sigma": witness["significant_violation_3sigma"],
        "record_hash_ok": pr.verify_record_hash(record),
        "bell_nonce_ok": pr.verify_bell_nonce(record, counts, cal, record["entropy_witness"]),
        "witness_matches_record": witness["S"] == record["entropy_witness"]["S"],
    }
    print(json.dumps(checks, indent=2))
    ok = (checks["record_hash_ok"] and checks["bell_nonce_ok"]
          and checks["witness_matches_record"])
    print("\nVERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
