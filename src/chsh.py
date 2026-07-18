"""
BELLWETHER-1 — CHSH Bell-inequality core.

Prepares the Bell state |Phi+> = (|00> + |11>)/sqrt(2) and measures the four
CHSH settings that maximize the S statistic (Tsirelson bound 2*sqrt(2) ~ 2.8284).

Measurement convention
----------------------
To measure the observable  cos(theta) Z + sin(theta) X  on a qubit, we apply
RY(-theta) and then measure in the computational (Z) basis. For |Phi+>:

    E(alpha, beta) = cos(alpha - beta)

CHSH:  S = E(a,b) - E(a,b') + E(a',b) + E(a',b')

Optimal angles used here (radians):
    a  = 0
    a' = pi/2
    b  = pi/4
    b' = 3*pi/4

  E(0,   pi/4)  = cos(-pi/4)      =  0.7071
  E(0,   3pi/4) = cos(-3pi/4)     = -0.7071   ->  -E = +0.7071
  E(pi/2,pi/4)  = cos(pi/4)       =  0.7071
  E(pi/2,3pi/4) = cos(-pi/4)      =  0.7071
  S = 4 * 0.7071 = 2.8284  (Tsirelson bound)

Classical/local-hidden-variable bound: |S| <= 2.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

# Canonical maximal-violation angles (radians)
A_ANGLES = [0.0, math.pi / 2]          # Alice: a, a'
B_ANGLES = [math.pi / 4, 3 * math.pi / 4]  # Bob:   b, b'

CLASSICAL_BOUND = 2.0
TSIRELSON_BOUND = 2.0 * math.sqrt(2.0)  # 2.8284271...

# The four (Alice, Bob) setting pairs, in the fixed order used everywhere.
# Order: (a,b), (a,b'), (a',b), (a',b')
SETTINGS: List[Tuple[float, float]] = [
    (A_ANGLES[0], B_ANGLES[0]),  # 0: (a, b)
    (A_ANGLES[0], B_ANGLES[1]),  # 1: (a, b')
    (A_ANGLES[1], B_ANGLES[0]),  # 2: (a', b)
    (A_ANGLES[1], B_ANGLES[1]),  # 3: (a', b')
]

# Sign vector applied to E-values when forming S:  +  -  +  +
S_SIGNS = [1.0, -1.0, 1.0, 1.0]


def build_circuits():
    """Return the four ISA-agnostic (logical) CHSH circuits, in SETTINGS order.

    Imported lazily so the module can be used for pure-math verification
    (mock tests / result recomputation) without qiskit present.
    """
    from qiskit import QuantumCircuit

    circuits = []
    for idx, (alpha, beta) in enumerate(SETTINGS):
        qc = QuantumCircuit(2, 2, name=f"chsh_{idx}")
        # Prepare |Phi+>
        qc.h(0)
        qc.cx(0, 1)
        # Rotate each qubit so the desired observable maps onto Z, then measure.
        qc.ry(-alpha, 0)
        qc.ry(-beta, 1)
        qc.barrier()
        qc.measure(0, 0)
        qc.measure(1, 1)
        circuits.append(qc)
    return circuits


def correlation_from_counts(counts: Dict[str, int]) -> float:
    """E = (N00 + N11 - N01 - N10) / N_total for one measurement setting.

    Bitstring keys may be "ab" (2 chars) with any endianness of a single
    2-qubit register; parity is endianness-invariant so E is unambiguous.
    """
    total = 0
    signed = 0
    for bitstr, n in counts.items():
        bits = bitstr.replace(" ", "")
        # take the two measured classical bits
        b = bits[-2:]
        parity_even = (b.count("1") % 2 == 0)  # 00 or 11 -> +1 ; 01 or 10 -> -1
        signed += n if parity_even else -n
        total += n
    if total == 0:
        raise ValueError("empty counts for a CHSH setting")
    return signed / total


def compute_S(counts_by_setting: List[Dict[str, int]]) -> Tuple[float, List[float]]:
    """Given four counts dicts in SETTINGS order, return (S, [E0,E1,E2,E3])."""
    if len(counts_by_setting) != 4:
        raise ValueError("expected exactly 4 counts dicts in SETTINGS order")
    E = [correlation_from_counts(c) for c in counts_by_setting]
    S = sum(sign * e for sign, e in zip(S_SIGNS, E))
    return S, E


def shot_noise_sigma_S(n_shots_per_setting: int) -> float:
    """Rough 1-sigma statistical uncertainty on S from shot noise.

    Each E is a mean of +/-1 outcomes: Var(E) <= (1 - E^2)/N <= 1/N.
    S is a sum of 4 independent E's, so Var(S) <= 4/N  => sigma_S <= 2/sqrt(N).
    This is a conservative (upper-bound) estimate reported honestly.
    """
    if n_shots_per_setting <= 0:
        raise ValueError("n_shots_per_setting must be positive")
    return 2.0 / math.sqrt(n_shots_per_setting)
