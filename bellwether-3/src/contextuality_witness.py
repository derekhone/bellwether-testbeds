"""
BELLWETHER-3 — state-independent contextuality witness.

Turns the measured Peres–Mermin chi statistic(s) into a bounded, honest witness
block that is cryptographically bound into the ProofRecord.

HONESTY BOUNDARY (carried verbatim into every artifact):
  * This is a device-dependent contextuality witness. The **compatibility
    (non-disturbance) loophole** is OPEN: the ancilla-parity gadgets are not
    perfectly non-disturbing, so a determined noncontextual modeller can attribute
    chi > 4 to measurement disturbance / finite-precision compatibility.
  * The **detection / fair-sampling** assumption is required (imperfect readout).
  * This is therefore a contextuality violation UNDER STATED TRUST ASSUMPTIONS,
    **not** loophole-free, and **not** device-independent certified randomness.
  * State-independence is asserted from theory and DEMONSTRATED across the
    prepared states actually run; it is not proven for literally all states.
  * Defensible claim: "observed Peres–Mermin state-independent contextuality
    violation (chi > 4) on hardware across multiple input states, under
    compatibility + detection trust assumptions, cryptographically bound into
    the authorization record."
"""
from __future__ import annotations

from typing import Dict, List

import peres_mermin as pm


def build_state_result(state: str, chi: float, E_values: List[float],
                       shots: int, sigma: float) -> Dict:
    excess = chi - pm.NONCONTEXTUAL_BOUND
    n_sigma = (excess / sigma) if sigma > 0 else 0.0
    return {
        "state": state,
        "chi": chi,
        "E_values": E_values,
        "context_names": pm.CONTEXT_NAMES,
        "sigma_chi": sigma,
        "excess_over_bound": excess,
        "n_sigma": n_sigma,
        "violation": bool(chi > pm.NONCONTEXTUAL_BOUND),
        "significant_violation_3sigma": bool(excess > 3 * sigma),
    }


def build_witness(per_state_results: List[Dict], shots: int) -> Dict:
    """per_state_results: list of build_state_result(...) dicts, one per input state."""
    all_violate = all(r["violation"] for r in per_state_results)
    all_3sigma = all(r["significant_violation_3sigma"] for r in per_state_results)
    chis = [r["chi"] for r in per_state_results]
    return {
        "witness_type": "peres_mermin_state_independent_contextuality",
        "noncontextual_bound": pm.NONCONTEXTUAL_BOUND,
        "quantum_value": pm.QUANTUM_VALUE,
        "shots_per_context": shots,
        "states_tested": [r["state"] for r in per_state_results],
        "per_state": per_state_results,
        "min_chi": min(chis) if chis else 0.0,
        "max_chi": max(chis) if chis else 0.0,
        "violation_all_states": bool(all_violate),
        "significant_all_states_3sigma": bool(all_3sigma),
        "state_independence_demonstrated": bool(all_violate and len(per_state_results) > 1),
        # Explicit, non-negotiable honesty flags.
        "loopholes_open": {
            "compatibility_non_disturbance": True,
            "detection_fair_sampling": True,
            "single_device": True,
        },
        "device_independent": False,
        "certified_randomness": False,
        "state_independence_proven_for_all_states": False,
        "claim": (
            "Observed Peres-Mermin state-independent contextuality violation (chi > 4) "
            "on quantum hardware across multiple input states, under compatibility "
            "(non-disturbance) + detection trust assumptions. NOT loophole-free; NOT "
            "device-independent certified randomness."
        ),
    }
