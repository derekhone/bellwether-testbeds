"""
BELLWETHER-2 — Mermin-3 inequality engine (3-qubit GHZ state).

We test the Mermin-Klyshko inequality for 3 qubits:

    M = ⟨A₁B₁C₁⟩ + ⟨A₁B₂C₂⟩ + ⟨A₂B₁C₂⟩ − ⟨A₂B₂C₁⟩

where A₁,A₂ are Alice's two measurement choices (σₓ, σᵧ), B₁,B₂ are Bob's, and
C₁,C₂ are Charlie's.

For the 3-qubit GHZ state |GHZ⟩ = (|000⟩ + |111⟩)/√2 and the standard Mermin
settings:
    A₁=X, A₂=Y,  B₁=Y, B₂=X,  C₁=Y, C₂=X

we get:
    - **Classical (local-realistic) bound:**  |M| ≤ 2
    - **Quantum GHZ prediction:**             M = 4

The four measurement circuits are X⊗Y⊗Y, Y⊗X⊗Y, Y⊗Y⊗X, X⊗X⊗X (notated as XYY, YXY, YYX, XXX).
Each 3-bit outcome (e.g. "101") maps to a parity: (-1)^(popcount). The
expectation value for a setting is the shot-average of parities.

Novelty vs. BELLWETHER-1:
    BELLWETHER-1:  2-qubit Bell+, CHSH (bipartite entanglement, S≈2.5)
    BELLWETHER-2:  3-qubit GHZ, Mermin-3 (genuine *multipartite* entanglement, M≈4)

Authorization angle: a multipartite witness (multiple independent parties must
jointly agree) — models multi-authority authorization.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

MERMIN_CLASSICAL_BOUND = 2.0
MERMIN_QUANTUM_MAX = 4.0

# The four Mermin-3 settings (order: qubit0, qubit1, qubit2).
SETTINGS = ["XYY", "YXY", "YYX", "XXX"]
MERMIN_COEFFS = [+1, +1, +1, -1]  # M = E(XYY) + E(YXY) + E(YYX) - E(XXX)


def build_circuits():
    """Return [qc_XYY, qc_YXY, qc_YYX, qc_XXX] as qiskit QuantumCircuits.

    Each circuit:
        1. Prepares the 3-qubit GHZ state (|000⟩+|111⟩)/√2.
        2. Rotates qubits to the measurement basis (X or Y).
        3. Measures all 3 qubits into a single 3-bit classical register 'c'.
    """
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

    def ghz_state(qc, qubits):
        """Prepare |GHZ⟩ = (|000⟩+|111⟩)/√2 on qubits [0,1,2]."""
        qc.h(qubits[0])
        qc.cx(qubits[0], qubits[1])
        qc.cx(qubits[1], qubits[2])

    def rotate_to_basis(qc, qubit, basis: str):
        """Apply rotation to measure in X or Y basis. Z is default."""
        if basis == "X":
            qc.h(qubit)
        elif basis == "Y":
            qc.sdg(qubit)
            qc.h(qubit)
        # Z basis: no rotation

    circuits = []
    for setting in SETTINGS:
        q = QuantumRegister(3, "q")
        c = ClassicalRegister(3, "c")
        qc = QuantumCircuit(q, c, name=setting)
        ghz_state(qc, q)
        for i, basis in enumerate(setting):
            rotate_to_basis(qc, q[i], basis)
        qc.measure(q, c)
        circuits.append(qc)
    return circuits


def parity_from_bitstring(bits: str) -> int:
    """Compute parity: (-1)^(number of '1's in bitstring).

    '000' → +1, '001' → -1, '010' → -1, '101' → +1, '111' → -1, etc.
    """
    return 1 if bits.count("1") % 2 == 0 else -1


def expectation_from_counts(counts: Dict[str, int]) -> float:
    """Shot-average of the 3-qubit parity.

    Counts keys are 3-character bitstrings (qiskit orders MSB=q[2], LSB=q[0]).
    Whitespace/other registers are stripped.
    """
    total = 0
    acc = 0.0
    for key, n in counts.items():
        bitstring = key.replace(" ", "")
        if len(bitstring) < 3:
            continue  # skip malformed keys
        # Take the 3 rightmost bits (c[2]c[1]c[0]).
        bits = bitstring[-3:]
        acc += n * parity_from_bitstring(bits)
        total += n
    if total == 0:
        return 0.0
    return acc / total


def compute_M(counts_list: List[Dict[str, int]]) -> Tuple[float, List[float]]:
    """counts_list is [counts_XYY, counts_YXY, counts_YYX, counts_XXX].

    Returns (M, [E_XYY, E_YXY, E_YYX, E_XXX]).
    """
    E = [expectation_from_counts(counts_list[i]) for i in range(4)]
    M = sum(MERMIN_COEFFS[i] * E[i] for i in range(4))
    return M, E


def shot_noise_sigma_M(E_values: List[float], shots: int) -> float:
    """Propagated 1-sigma statistical uncertainty on M.

    Var(E) = (1 - E²)/N for a dichotomic observable (±1).
    M = E₁ + E₂ + E₃ - E₄, so variances add (coefficients squared are all 1).
    """
    var = sum(max(0.0, (1.0 - e * e)) / max(1, shots) for e in E_values)
    return math.sqrt(var)
