"""
BELLWETHER-2 — multipartite entanglement witness.

Turns the measured Mermin-3 statistic M into a bounded, honest witness block
that is cryptographically bound into the ProofRecord.

HONESTY BOUNDARY (carried verbatim into every artifact):
  * This is a device-dependent witness on co-located qubits. The **locality
    loophole** (qubits on the same chip can communicate classically) and
    **detection loophole** (imperfect readout) are OPEN.
  * This is therefore a Mermin violation UNDER STATED TRUST ASSUMPTIONS,
    **not** loophole-free, and **not** device-independent certified randomness.
  * Defensible claim: "observed 3-qubit Mermin inequality violation (genuine
    multipartite entanglement) on hardware, under locality + detection trust
    assumptions, cryptographically bound into the authorization record."
"""
from __future__ import annotations

from typing import Dict, List

import mermin


def build_witness(M: float, E_values: List[float], shots: int, sigma: float) -> Dict:
    excess = abs(M) - mermin.MERMIN_CLASSICAL_BOUND
    n_sigma = (excess / sigma) if sigma > 0 else 0.0
    witness = {
        "witness_type": "mermin_3qubit_multipartite",
        "M": M,
        "E_values": E_values,
        "settings": mermin.SETTINGS,
        "classical_bound": mermin.MERMIN_CLASSICAL_BOUND,
        "quantum_max": mermin.MERMIN_QUANTUM_MAX,
        "shots_per_setting": shots,
        "sigma_M": sigma,
        "excess_over_bound": excess,
        "n_sigma": n_sigma,
        "violation": bool(abs(M) > mermin.MERMIN_CLASSICAL_BOUND),
        "significant_violation_3sigma": bool(excess > 3 * sigma),
        # Explicit, non-negotiable honesty flags.
        "loopholes_open": {
            "locality": True,
            "detection": True,
            "co_located_qubits": True,
        },
        "device_independent": False,
        "certified_randomness": False,
        "claim": (
            "Observed 3-qubit Mermin inequality violation (genuine multipartite "
            "entanglement) on quantum hardware, under locality + detection trust "
            "assumptions. NOT loophole-free; NOT device-independent certified randomness."
        ),
    }
    return witness
