"""
BELLWETHER-3 — Peres–Mermin magic-square engine (state-independent contextuality).

RESOURCE JUMP (vs. prior series):
    BELLWETHER-1  2-qubit CHSH        -> spatial nonlocality (bipartite entanglement)
    BELLWETHER-2  3-qubit GHZ Mermin  -> spatial nonlocality (multipartite entanglement)
    CHRONO-1      Leggett–Garg K3     -> temporal nonclassicality
    BELLWETHER-3  Peres–Mermin square -> **quantum CONTEXTUALITY** (a distinct resource;
                                          needs NO entanglement, NO spatial separation,
                                          and is STATE-INDEPENDENT).

Contextuality is the resource behind quantum computational advantage (magic-state
distillation). This is, to our knowledge, the first time a *state-independent
contextuality* witness is cryptographically bound into an authorization record.

--------------------------------------------------------------------------------
THE PERES–MERMIN SQUARE
--------------------------------------------------------------------------------
A 3x3 grid of two-qubit Pauli observables. Every row and every column consists of
three MUTUALLY COMMUTING observables. The product of the three observables in each
row and in the first two columns is +II; the product in the third column is -II:

           col1      col2      col3        row product
   row1    X·I       I·X       X·X          +II
   row2    I·Z       Z·I       Z·Z          +II
   row3    X·Z       Z·X       Y·Y          +II
   colprod +II       +II       -II

No noncontextual hidden-variable model can assign definite ±1 values v(O) to all
nine observables consistent with all six product constraints (the six products
multiply to -I, but each observable appears in exactly one row and one column so
any value assignment forces the six products to multiply to +I — a contradiction).

CONTEXTUALITY FUNCTIONAL:
    chi = <R1> + <R2> + <R3> + <C1> + <C2> - <C3>

where <Ck> is the expectation of the PRODUCT of the three individually- and
compatibly-measured outcomes in that context.

    * Noncontextual (classical) bound:  chi <= 4
    * Quantum prediction:               chi  = 6   (for ANY input state)

--------------------------------------------------------------------------------
HOW EACH CONTEXT IS MEASURED (compatible, non-disturbing)
--------------------------------------------------------------------------------
The three observables in a context commute, so they can be measured jointly. We
read each observable's ±1 eigenvalue with an ancilla via a Hadamard-test parity
gadget:  ancilla |0> -> H -> controlled-(P0 on q0, P1 on q1) -> H -> measure.
Outcome bit b gives eigenvalue (-1)^b. Three observables -> three ancillas ->
three bits per shot. The context correlator per shot is the product of the three
eigenvalues = (-1)^(b0+b1+b2). Because the observables commute, the three gadgets
commute and implement a genuine simultaneous (compatible) measurement.

On a noiseless simulator every shot yields the product-operator eigenvalue exactly,
so chi = 6. On hardware, gate/readout error pulls chi below 6; chi > 4 (at >3 sigma)
is the contextuality signature (under the stated measurement assumptions).

STATE-INDEPENDENCE: chi = 6 holds for every input state. We exploit this by
running the full square on MULTIPLE preparations (e.g. |00>, |++>, a Bell state)
and showing chi > 4 for each — a robustness property with direct authorization value.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

NONCONTEXTUAL_BOUND = 4.0
QUANTUM_VALUE = 6.0

# Each observable is a 2-char Pauli string acting on (data qubit 0, data qubit 1).
# "I" = identity, "X"/"Y"/"Z" = Pauli.
# The six contexts, in the fixed order used everywhere downstream.
CONTEXTS: List[Dict] = [
    {"name": "R1", "obs": ["XI", "IX", "XX"], "coeff": +1, "ideal": +1},
    {"name": "R2", "obs": ["IZ", "ZI", "ZZ"], "coeff": +1, "ideal": +1},
    {"name": "R3", "obs": ["XZ", "ZX", "YY"], "coeff": +1, "ideal": +1},
    {"name": "C1", "obs": ["XI", "IZ", "XZ"], "coeff": +1, "ideal": +1},
    {"name": "C2", "obs": ["IX", "ZI", "ZX"], "coeff": +1, "ideal": +1},
    {"name": "C3", "obs": ["XX", "ZZ", "YY"], "coeff": -1, "ideal": -1},
]

CONTEXT_NAMES = [c["name"] for c in CONTEXTS]
CONTEXT_COEFFS = [c["coeff"] for c in CONTEXTS]

# Supported input-state preparations (all give chi = 6; demonstrates state-independence).
STATES = {
    "00": [],                          # computational |00>
    "++": [("h", 0), ("h", 1)],        # |++>
    "bell": [("h", 0), ("cx", 0, 1)],  # (|00>+|11>)/sqrt2  (entangled)
}


def _apply_state_prep(qc, q, state: str):
    for op in STATES[state]:
        if op[0] == "h":
            qc.h(q[op[1]])
        elif op[0] == "cx":
            qc.cx(q[op[1]], q[op[2]])
        else:
            raise ValueError(f"unknown prep op {op}")


def _controlled_pauli(qc, anc, data_qubits, pauli: str):
    """Apply controlled-(P0 on q0, P1 on q1) with ancilla `anc` as control."""
    for i, p in enumerate(pauli):
        tq = data_qubits[i]
        if p == "I":
            continue
        elif p == "X":
            qc.cx(anc, tq)
        elif p == "Y":
            qc.cy(anc, tq)
        elif p == "Z":
            qc.cz(anc, tq)
        else:
            raise ValueError(f"unknown pauli letter {p}")


def build_context_circuit(context: Dict, state: str = "00"):
    """One circuit measuring the three commuting observables of `context`
    on data-state `state`, via three Hadamard-test ancilla parity gadgets.

    Layout: q[0],q[1] = data; q[2],q[3],q[4] = ancillas for obs[0],obs[1],obs[2].
    Classical register c[0..2] holds the three ancilla outcomes.
    """
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

    q = QuantumRegister(5, "q")
    c = ClassicalRegister(3, "c")
    qc = QuantumCircuit(q, c, name=f"{context['name']}_{state}")
    data = [q[0], q[1]]

    _apply_state_prep(qc, q, state)
    qc.barrier()

    for k, obs in enumerate(context["obs"]):
        anc = q[2 + k]
        qc.h(anc)
        _controlled_pauli(qc, anc, data, obs)
        qc.h(anc)
    qc.barrier()

    for k in range(3):
        qc.measure(q[2 + k], c[k])
    return qc


def build_all_circuits(states: List[str] = None):
    """Return (circuits, index) where index[i] = (state, context_name).

    Circuits are ordered state-major: for each state, the six contexts in order.
    """
    if states is None:
        states = ["00"]
    circuits = []
    index = []
    for state in states:
        for ctx in CONTEXTS:
            circuits.append(build_context_circuit(ctx, state))
            index.append((state, ctx["name"]))
    return circuits, index


def parity_from_bitstring(bits: str) -> int:
    """(-1)^(number of 1s) over the three ancilla outcome bits."""
    return 1 if bits.count("1") % 2 == 0 else -1


def expectation_from_counts(counts: Dict[str, int]) -> float:
    """Shot-average of the 3-ancilla parity = <product of the three outcomes>."""
    total = 0
    acc = 0.0
    for key, n in counts.items():
        bits = key.replace(" ", "")
        if len(bits) < 3:
            continue
        acc += n * parity_from_bitstring(bits[-3:])
        total += n
    return acc / total if total else 0.0


def compute_chi_for_state(counts_by_context: List[Dict[str, int]]) -> Tuple[float, List[float]]:
    """counts_by_context is the six contexts (R1,R2,R3,C1,C2,C3) for ONE state.

    Returns (chi, [E_R1, E_R2, E_R3, E_C1, E_C2, E_C3]).
    """
    E = [expectation_from_counts(counts_by_context[i]) for i in range(6)]
    chi = sum(CONTEXT_COEFFS[i] * E[i] for i in range(6))
    return chi, E


def shot_noise_sigma_chi(E_values: List[float], shots: int) -> float:
    """1-sigma statistical uncertainty on chi.

    Each context correlator is a dichotomic (+-1) mean: Var(E)=(1-E^2)/N.
    chi is a signed sum of the six (coeffs are +-1, so squared coeffs are 1),
    so the variances add.
    """
    var = sum(max(0.0, (1.0 - e * e)) / max(1, shots) for e in E_values)
    return math.sqrt(var)
