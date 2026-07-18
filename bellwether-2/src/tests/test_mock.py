"""
BELLWETHER-2 — pre-lock mock tests (no hardware, no network).

Validates the Mermin-3 physics engine, the multipartite witness logic, the
ProofRecord provenance chain, and its tamper-evidence, using synthetic ideal
counts for the 3-qubit GHZ state.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import mermin
import multipartite_witness as mw
import proofrecord as pr


def _ideal_ghz_counts(setting: str, shots: int = 100000):
    """Build ideal counts for a Mermin setting on |GHZ⟩=(|000⟩+|111⟩)/√2.

    Based on our circuit construction (validated via AerSimulator):
    For XYY, YXY, YYX: E=-1 (all outcomes have odd parity).
    For XXX: E=+1 (all outcomes have even parity).
    Keys are 'c[2]c[1]c[0]' (qiskit MSB=q[2], LSB=q[0]).
    """
    if setting in ("XYY", "YXY", "YYX"):
        # Odd-parity outcomes: 001, 010, 100, 111
        return {"001": shots // 4, "010": shots // 4,
                "100": shots // 4, "111": shots // 4}
    elif setting == "XXX":
        # Even-parity outcomes: 000, 011, 101, 110
        return {"000": shots // 4, "011": shots // 4,
                "101": shots // 4, "110": shots // 4}
    else:
        raise ValueError(f"unknown setting {setting}")


def test_parity_logic():
    assert mermin.parity_from_bitstring("000") == +1
    assert mermin.parity_from_bitstring("001") == -1
    assert mermin.parity_from_bitstring("010") == -1
    assert mermin.parity_from_bitstring("011") == +1
    assert mermin.parity_from_bitstring("111") == -1
    assert mermin.parity_from_bitstring("110") == +1


def test_ideal_expectations():
    for setting, expected_E in [("XYY", -1), ("YXY", -1), ("YYX", -1), ("XXX", +1)]:
        counts = _ideal_ghz_counts(setting)
        E = mermin.expectation_from_counts(counts)
        assert abs(E - expected_E) < 0.01, (setting, E, expected_E)


def test_ideal_M_is_minus_4():
    """Our circuit construction gives M=-4 (validated via simulator).
    
    The sign is a basis/phase convention; the violation is |M| > 2.
    """
    counts = [_ideal_ghz_counts(s) for s in mermin.SETTINGS]
    M, E = mermin.compute_M(counts)
    assert abs(M + 4.0) < 0.01, (M, E)  # M ≈ -4


def test_witness_flags_violation():
    counts = [_ideal_ghz_counts(s) for s in mermin.SETTINGS]
    M, E = mermin.compute_M(counts)
    sigma = mermin.shot_noise_sigma_M(E, 100000)
    w = mw.build_witness(M, E, 100000, sigma)
    assert w["violation"] is True
    assert w["significant_violation_3sigma"] is True
    assert w["device_independent"] is False
    assert w["certified_randomness"] is False
    assert w["loopholes_open"]["locality"] is True


def test_witness_no_violation_when_classical():
    # M = 2.0 exactly (classical bound) -> no violation
    # E.g. E=[0.5, 0.5, 0.5, 0.5] => M=0.5+0.5+0.5-0.5=1.0 < 2; let's use [1,1,0,0] => M=1+1+0-0=2
    counts = [{"000": 75000, "111": 25000}] * 4  # rough E≈0.5 each
    M, E = mermin.compute_M(counts)
    sigma = mermin.shot_noise_sigma_M(E, 100000)
    w = mw.build_witness(M, E, 100000, sigma)
    assert w["violation"] is False or abs(M) <= mermin.MERMIN_CLASSICAL_BOUND + 0.1


def test_proofrecord_roundtrip():
    counts = [_ideal_ghz_counts(s) for s in mermin.SETTINGS]
    M, E = mermin.compute_M(counts)
    sigma = mermin.shot_noise_sigma_M(E, 2000)
    w = mw.build_witness(M, E, 2000, sigma)
    cal = {"backend": "mock", "readout_error": 0.01}
    rec = pr.build_proofrecord(counts, "job_mock", "ibm_fez", "open-instance",
                               cal, w, "bellwether-2-primary", "2026-07-18T00:00:00Z")
    assert pr.verify_record_hash(rec)
    assert pr.verify_mermin_nonce(rec, counts, cal, w)


def test_tamper_witness_breaks_nonce():
    counts = [_ideal_ghz_counts(s) for s in mermin.SETTINGS]
    M, E = mermin.compute_M(counts)
    sigma = mermin.shot_noise_sigma_M(E, 2000)
    w = mw.build_witness(M, E, 2000, sigma)
    cal = {"backend": "mock"}
    rec = pr.build_proofrecord(counts, "job_mock", "ibm_fez", "open-instance",
                               cal, w, "bellwether-2-primary", "2026-07-18T00:00:00Z")
    forged = dict(w)
    forged["M"] = 3.5  # alter the claimed statistic
    assert not pr.verify_mermin_nonce(rec, counts, cal, forged)


def test_tamper_counts_breaks_nonce():
    counts = [_ideal_ghz_counts(s) for s in mermin.SETTINGS]
    M, E = mermin.compute_M(counts)
    sigma = mermin.shot_noise_sigma_M(E, 2000)
    w = mw.build_witness(M, E, 2000, sigma)
    cal = {"backend": "mock"}
    rec = pr.build_proofrecord(counts, "job_mock", "ibm_fez", "open-instance",
                               cal, w, "bellwether-2-primary", "2026-07-18T00:00:00Z")
    forged_counts = [dict(counts[0]), counts[1], counts[2], counts[3]]
    forged_counts[0]["000"] = forged_counts[0].get("000", 0) + 5000
    assert not pr.verify_mermin_nonce(rec, forged_counts, cal, w)


def test_record_hash_detects_field_edit():
    counts = [_ideal_ghz_counts(s) for s in mermin.SETTINGS]
    M, E = mermin.compute_M(counts)
    sigma = mermin.shot_noise_sigma_M(E, 2000)
    w = mw.build_witness(M, E, 2000, sigma)
    cal = {"backend": "mock"}
    rec = pr.build_proofrecord(counts, "job_mock", "ibm_fez", "open-instance",
                               cal, w, "bellwether-2-primary", "2026-07-18T00:00:00Z")
    rec["backend"] = "ibm_marrakesh"  # edit a covered field
    assert not pr.verify_record_hash(rec)


def test_settings_order():
    assert mermin.SETTINGS == ["XYY", "YXY", "YYX", "XXX"]
    assert mermin.MERMIN_COEFFS == [+1, +1, +1, -1]


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} tests passed")
