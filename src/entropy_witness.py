"""
BELLWETHER-1 — entropy witness.

Turns a measured CHSH S value into an *illustrative* randomness bound and a
violation verdict. This is the novel layer: a ProofRecord field that carries a
physical witness of the nonclassical correlation that produced the nonce.

CRITICAL HONESTY BOUNDARY (carried into every artifact)
-------------------------------------------------------
The standard device-independent (DI) relationship between the CHSH value S and
the adversary guessing probability of the local outcomes is:

    P_guess(S) <= 1/2 * ( 1 + sqrt( 2 - S^2 / 4 ) )         for  2 <= S <= 2*sqrt(2)

and the corresponding min-entropy per measured pair:

    H_min = -log2( P_guess )

BUT this DI bound is only physically meaningful when the locality and detection
loopholes are CLOSED. On a single superconducting chip:

  * both qubits are co-located and measured together  -> LOCALITY loophole OPEN
  * readout is imperfect and post-selection-free but not fair-sampling-certified
        -> DETECTION loophole OPEN
  * outcomes may share classical common causes via the shared control system

Therefore the number returned here is a DEVICE-DEPENDENT, ASSUMPTION-LADEN
witness, NOT a loophole-free certified-randomness guarantee. It is reported as
"illustrative_min_entropy_bits" with loopholes_open=True so no reader can mistake
it for DI certification. The honest, defensible claim is only:

    "We observed a CHSH value S = <...> > 2, a Bell-inequality violation on
     hardware under stated trust assumptions, and cryptographically bound that
     statistic into the authorization record."
"""
from __future__ import annotations

import math
from typing import Optional

CLASSICAL_BOUND = 2.0
TSIRELSON_BOUND = 2.0 * math.sqrt(2.0)


def guessing_probability(S: float) -> Optional[float]:
    """DI guessing-probability upper bound as a function of S (2 <= S <= 2sqrt2).

    Returns None when S <= 2 (no violation -> no nontrivial bound).
    Clamps S to the Tsirelson bound to keep the sqrt real under shot noise.
    """
    if S <= CLASSICAL_BOUND:
        return None
    s = min(S, TSIRELSON_BOUND)
    inner = 2.0 - (s * s) / 4.0
    inner = max(inner, 0.0)  # guard tiny negative from float error near Tsirelson
    return 0.5 * (1.0 + math.sqrt(inner))


def illustrative_min_entropy_bits(S: float) -> Optional[float]:
    """H_min = -log2(P_guess). Illustrative only (loopholes open)."""
    pg = guessing_probability(S)
    if pg is None or pg <= 0.0:
        return None
    return -math.log2(pg)


def build_witness(S: float, E: list, n_shots_per_setting: int,
                  sigma_S: float) -> dict:
    """Assemble the entropy-witness sub-record with explicit caveats."""
    violation = S > CLASSICAL_BOUND
    # Statistically-guarded violation: require S - 2 to exceed 3 sigma.
    significant_violation = (S - CLASSICAL_BOUND) > (3.0 * sigma_S)
    return {
        "statistic": "CHSH",
        "S": S,
        "E_values": list(E),
        "classical_bound": CLASSICAL_BOUND,
        "tsirelson_bound": TSIRELSON_BOUND,
        "violation": bool(violation),
        "significant_violation_3sigma": bool(significant_violation),
        "sigma_S_shot_noise": sigma_S,
        "n_shots_per_setting": n_shots_per_setting,
        "illustrative_min_entropy_bits": illustrative_min_entropy_bits(S),
        "loopholes_open": True,
        "certification_class": "device-dependent witness (NOT loophole-free / NOT DI)",
        "honesty_note": (
            "Co-located qubits leave the locality loophole open and readout "
            "leaves the detection loophole open. The min-entropy figure is "
            "illustrative under trust assumptions, not a device-independent "
            "certified-randomness guarantee."
        ),
    }
