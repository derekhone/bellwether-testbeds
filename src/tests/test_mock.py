"""
BELLWETHER-1 pre-lock mock tests. No QPU required.

Run: python3 -m pytest src/tests/test_mock.py -q
 or: python3 src/tests/test_mock.py
"""
from __future__ import annotations

import math
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import chsh
import entropy_witness as ew
import proofrecord as pr


def ideal_counts(alpha: float, beta: float, n: int) -> dict:
    """Ideal |Phi+> counts for a setting: E = cos(alpha-beta)."""
    E = math.cos(alpha - beta)
    p_same = (1.0 + E) / 2.0
    n00 = round(n * p_same / 2.0)
    n11 = round(n * p_same / 2.0)
    n01 = round(n * (1.0 - p_same) / 2.0)
    n10 = n - n00 - n11 - n01
    return {"00": n00, "01": n01, "10": n10, "11": n11}


def ideal_counts_all(n: int):
    return [ideal_counts(a, b, n) for (a, b) in chsh.SETTINGS]


def test_ideal_S_near_tsirelson():
    counts = ideal_counts_all(200000)
    S, E = chsh.compute_S(counts)
    assert abs(S - chsh.TSIRELSON_BOUND) < 0.02, f"S={S}"
    assert S > 2.0


def test_classical_strategy_bounded():
    # Deterministic classical strategy: always output 00 -> E=+1 every setting.
    # S = 1 - 1 + 1 + 1 = 2  (saturates but does not exceed classical bound).
    counts = [{"00": 1000, "01": 0, "10": 0, "11": 0} for _ in chsh.SETTINGS]
    S, _ = chsh.compute_S(counts)
    assert S <= 2.0 + 1e-9, f"classical S={S} must not exceed 2"


def test_correlation_signs():
    # E(0, pi/4) should be +cos(pi/4); E(0, 3pi/4) should be -cos(pi/4).
    c0 = ideal_counts(0.0, math.pi / 4, 100000)
    c1 = ideal_counts(0.0, 3 * math.pi / 4, 100000)
    assert chsh.correlation_from_counts(c0) > 0.6
    assert chsh.correlation_from_counts(c1) < -0.6


def test_entropy_witness_violation():
    counts = ideal_counts_all(4000)
    S, E = chsh.compute_S(counts)
    sigma = chsh.shot_noise_sigma_S(4000)
    w = ew.build_witness(S, E, 4000, sigma)
    assert w["violation"] is True
    assert w["significant_violation_3sigma"] is True
    assert w["loopholes_open"] is True
    assert w["illustrative_min_entropy_bits"] is not None
    assert 0.0 < w["illustrative_min_entropy_bits"] <= 1.0


def test_no_violation_gives_no_entropy():
    # S exactly at classical bound -> no nontrivial bound.
    assert ew.guessing_probability(2.0) is None
    assert ew.illustrative_min_entropy_bits(2.0) is None


def test_proofrecord_roundtrip():
    counts = ideal_counts_all(4000)
    S, E = chsh.compute_S(counts)
    sigma = chsh.shot_noise_sigma_S(4000)
    w = ew.build_witness(S, E, 4000, sigma)
    cal = {"backend": "mock", "t": 1, "gate_err": 0.001}
    rec = pr.build_proofrecord(counts, "job_mock", "mock_backend",
                               "mock_instance", cal, w, "bellwether-1-primary",
                               "2026-07-18T00:00:00Z")
    assert pr.verify_record_hash(rec)
    assert pr.verify_bell_nonce(rec, counts, cal, w)


def test_tamper_breaks_record():
    counts = ideal_counts_all(4000)
    S, E = chsh.compute_S(counts)
    sigma = chsh.shot_noise_sigma_S(4000)
    w = ew.build_witness(S, E, 4000, sigma)
    cal = {"backend": "mock", "t": 1}
    rec = pr.build_proofrecord(counts, "job_mock", "mock_backend",
                               "mock_instance", cal, w, "ctx", "2026-07-18T00:00:00Z")

    # (a) tamper a raw count -> bell_nonce & record must fail to reverify
    tampered = [dict(c) for c in counts]
    tampered[0]["00"] += 1
    assert not pr.verify_bell_nonce(rec, tampered, cal, w)

    # (b) forge the witness S upward -> witness_hash changes -> nonce breaks
    forged = dict(w)
    forged["S"] = 2.9
    assert not pr.verify_bell_nonce(rec, counts, cal, forged)

    # (c) edit a field in the record body -> record_hash breaks
    bad = dict(rec)
    bad["backend"] = "someone_elses_backend"
    assert not pr.verify_record_hash(bad)


def test_shot_noise_sigma_monotonic():
    assert chsh.shot_noise_sigma_S(1000) > chsh.shot_noise_sigma_S(4000)


def _run():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn()
        passed += 1
        print(f"PASS  {fn.__name__}")
    print(f"\n{passed}/{len(fns)} mock tests PASS")


if __name__ == "__main__":
    _run()
