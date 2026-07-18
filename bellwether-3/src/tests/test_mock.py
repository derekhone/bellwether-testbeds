"""
BELLWETHER-3 — pre-lock mock tests (no hardware, no network).

Validates the Peres–Mermin engine, the contextuality witness logic, the
ProofRecord provenance chain, and its tamper-evidence, using synthetic ideal
counts (each context correlator = its product-operator eigenvalue).
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import peres_mermin as pm
import contextuality_witness as cw
import proofrecord as pr


def _ideal_context_counts(ideal_value: int, shots: int = 10000):
    """Counts whose 3-ancilla parity averages to `ideal_value` (+1 or -1).

    parity=+1 -> even # of 1s (000,011,101,110); parity=-1 -> odd (001,010,100,111).
    """
    if ideal_value == +1:
        return {"000": shots // 4, "011": shots // 4,
                "101": shots // 4, "110": shots // 4}
    else:
        return {"001": shots // 4, "010": shots // 4,
                "100": shots // 4, "111": shots // 4}


def _ideal_counts_for_state(shots=10000):
    return [_ideal_context_counts(c["ideal"], shots) for c in pm.CONTEXTS]


def _ideal_payload(states, shots=10000):
    return {"counts_by_state": {s: _ideal_counts_for_state(shots) for s in states},
            "states": states, "context_order": pm.CONTEXT_NAMES}


def test_parity_logic():
    assert pm.parity_from_bitstring("000") == +1
    assert pm.parity_from_bitstring("001") == -1
    assert pm.parity_from_bitstring("111") == -1
    assert pm.parity_from_bitstring("110") == +1


def test_context_definitions():
    assert pm.CONTEXT_NAMES == ["R1", "R2", "R3", "C1", "C2", "C3"]
    assert pm.CONTEXT_COEFFS == [+1, +1, +1, +1, +1, -1]
    # every observable appears once per row and once per column
    rows = [set(pm.CONTEXTS[i]["obs"]) for i in range(3)]
    cols = [set(pm.CONTEXTS[i]["obs"]) for i in range(3, 6)]
    all_obs = set().union(*rows)
    assert len(all_obs) == 9  # nine distinct observables


def test_ideal_chi_is_6():
    counts = _ideal_counts_for_state()
    chi, E = pm.compute_chi_for_state(counts)
    assert abs(chi - 6.0) < 1e-6, (chi, E)
    assert E == [1.0, 1.0, 1.0, 1.0, 1.0, -1.0]


def test_witness_flags_violation_all_states():
    states = ["00", "++", "bell"]
    results = []
    for s in states:
        counts = _ideal_counts_for_state()
        chi, E = pm.compute_chi_for_state(counts)
        sigma = pm.shot_noise_sigma_chi(E, 10000)
        results.append(cw.build_state_result(s, chi, E, 10000, sigma))
    w = cw.build_witness(results, 10000)
    assert w["violation_all_states"] is True
    assert w["significant_all_states_3sigma"] is True
    assert w["state_independence_demonstrated"] is True
    assert w["device_independent"] is False
    assert w["certified_randomness"] is False
    assert w["loopholes_open"]["compatibility_non_disturbance"] is True


def test_noncontextual_bound_not_violated_when_classical():
    # Force a classical-like assignment: make one context correlator wrong so chi<=4.
    # Set C3 to +1 (its ideal is -1): chi = 1+1+1+1+1 - (+1) = 4  -> no violation.
    counts = _ideal_counts_for_state()
    counts[5] = _ideal_context_counts(+1)  # C3 forced +1
    chi, E = pm.compute_chi_for_state(counts)
    assert abs(chi - 4.0) < 1e-6, (chi, E)
    sigma = pm.shot_noise_sigma_chi(E, 10000)
    r = cw.build_state_result("00", chi, E, 10000, sigma)
    assert r["violation"] is False


def test_proofrecord_roundtrip():
    states = ["00", "++"]
    payload = _ideal_payload(states)
    results = []
    for s in states:
        chi, E = pm.compute_chi_for_state(payload["counts_by_state"][s])
        sigma = pm.shot_noise_sigma_chi(E, 10000)
        results.append(cw.build_state_result(s, chi, E, 10000, sigma))
    w = cw.build_witness(results, 10000)
    cal = {"backend": "mock"}
    rec = pr.build_proofrecord(payload, "job_mock", "ibm_fez", "open-instance",
                               cal, w, "bellwether-3-primary", "2026-07-18T00:00:00Z")
    assert pr.verify_record_hash(rec)
    assert pr.verify_context_nonce(rec, payload, cal, w)


def test_tamper_witness_breaks_nonce():
    states = ["00"]
    payload = _ideal_payload(states)
    chi, E = pm.compute_chi_for_state(payload["counts_by_state"]["00"])
    sigma = pm.shot_noise_sigma_chi(E, 10000)
    w = cw.build_witness([cw.build_state_result("00", chi, E, 10000, sigma)], 10000)
    cal = {"backend": "mock"}
    rec = pr.build_proofrecord(payload, "job_mock", "ibm_fez", "open-instance",
                               cal, w, "bellwether-3-primary", "2026-07-18T00:00:00Z")
    forged = json._default_decoder.decode(json.dumps(w)) if False else dict(w)
    forged["max_chi"] = 5.9  # alter claimed statistic
    assert not pr.verify_context_nonce(rec, payload, cal, forged)


def test_tamper_counts_breaks_nonce():
    states = ["00"]
    payload = _ideal_payload(states)
    chi, E = pm.compute_chi_for_state(payload["counts_by_state"]["00"])
    sigma = pm.shot_noise_sigma_chi(E, 10000)
    w = cw.build_witness([cw.build_state_result("00", chi, E, 10000, sigma)], 10000)
    cal = {"backend": "mock"}
    rec = pr.build_proofrecord(payload, "job_mock", "ibm_fez", "open-instance",
                               cal, w, "bellwether-3-primary", "2026-07-18T00:00:00Z")
    import copy
    forged = copy.deepcopy(payload)
    forged["counts_by_state"]["00"][0]["000"] += 5000
    assert not pr.verify_context_nonce(rec, forged, cal, w)


def test_record_hash_detects_field_edit():
    states = ["00"]
    payload = _ideal_payload(states)
    chi, E = pm.compute_chi_for_state(payload["counts_by_state"]["00"])
    sigma = pm.shot_noise_sigma_chi(E, 10000)
    w = cw.build_witness([cw.build_state_result("00", chi, E, 10000, sigma)], 10000)
    cal = {"backend": "mock"}
    rec = pr.build_proofrecord(payload, "job_mock", "ibm_fez", "open-instance",
                               cal, w, "bellwether-3-primary", "2026-07-18T00:00:00Z")
    rec["backend"] = "ibm_marrakesh"
    assert not pr.verify_record_hash(rec)


def test_circuits_build():
    circuits, index = pm.build_all_circuits(["00", "++", "bell"])
    assert len(circuits) == 18
    assert len(index) == 18
    # each circuit has 5 qubits, 3 clbits
    for qc in circuits:
        assert qc.num_qubits == 5
        assert qc.num_clbits == 3


import json  # noqa: E402 (used by one test)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} tests passed")
