# BELLWETHER-3 — Preregistration

**Series:** BELLWETHER (spatial / measurement nonclassicality)
**Experiment ID:** BELLWETHER-3 *(3rd in the BELLWETHER series; 4th RF quantum flagship overall — after BELLWETHER-1, CHRONO-1, BELLWETHER-2)*
**Title:** *Peres–Mermin Magic Square — State-Independent Quantum Contextuality bound into an authorization ProofRecord*
**Owner:** Remnant Fieldworks Inc. (Derek Adam Hone)
**Status at lock:** design + harness complete, validated in simulation (χ = 6.000 across three input states), hardware job pending
**Governing framework:** RF Experiment–Pilot–IP Covenant (preregistration-first; honest outcomes; claims narrower than evidence; file-first / publish-after for new matter)

---

## 1. One-sentence statement

We measure the **Peres–Mermin magic-square contextuality functional χ** on two qubits, show it exceeds the noncontextual bound **for every input state we prepare**, and **cryptographically bind the measured χ (and its state-independence) into an authorization ProofRecord** — the first authorization primitive whose physical witness is *quantum contextuality*, the resource that fuels quantum computational advantage.

## 2. Why this is world-class — a new *resource*, not a bigger number

RF's prior flagships all witnessed **nonlocality** or **temporal** nonclassicality. BELLWETHER-3 crosses into a **distinct and deeper physical resource: contextuality.**

| RF flagship | State / system | Test | Resource witnessed | Needs entanglement? |
|-------------|----------------|------|--------------------|---------------------|
| BELLWETHER-1 | 2-qubit Bell⁺ | CHSH (S>2) | bipartite nonlocality | yes |
| BELLWETHER-2 | 3-qubit GHZ | Mermin-3 (\|M\|>2) | multipartite nonlocality | yes |
| CHRONO-1 | 1 qubit, mid-circuit | Leggett–Garg (K3>1) | temporal nonclassicality | no |
| **BELLWETHER-3** | **2 qubits + ancillas** | **Peres–Mermin (χ>4)** | **contextuality (state-independent)** | **no** |

**Three reasons this is a genuine frontier result:**

1. **Contextuality is the fuel of quantum advantage.** Contextuality — not entanglement — is the property proven necessary for universal quantum computation via magic-state distillation (Howard et al., *Nature* 2014). Binding *this* resource into an authorization record ties RF's ExecutionProof program directly to the deepest known quantum-computational resource.

2. **State-independence.** The Peres–Mermin violation (χ = 6 > 4) holds for **every** input state — pure, mixed, product, or entangled. We demonstrate it across |00⟩, |++⟩, and an entangled Bell state. No prior RF witness had this property: it means the authorization certificate is **robust to whatever state a preparation adversary supplies.**

3. **Nonlocality-free.** The witness requires **no entanglement and no spatial separation** — it is a property of the *measurement algebra itself*. This is a fundamentally different (and harder-to-explain-away) form of nonclassicality than a Bell test, and it is, to our knowledge, **never before bound into a cryptographic authorization record.**

## 3. Physics and design

**The Peres–Mermin square** — nine two-qubit Pauli observables in a 3×3 grid; each row and column is a set of three mutually commuting observables:

|        | col 1 | col 2 | col 3 | row product |
|--------|-------|-------|-------|-------------|
| **row 1** | X·I | I·X | X·X | +II |
| **row 2** | I·Z | Z·I | Z·Z | +II |
| **row 3** | X·Z | Z·X | Y·Y | +II |
| **col product** | +II | +II | **−II** | |

Five contexts multiply to +II and one (column 3) to −II. No noncontextual hidden-variable model can assign definite ±1 values to all nine observables consistent with all six product constraints (the six products would have to multiply to both +I *and* −I).

**Contextuality functional:**

    χ = ⟨R1⟩ + ⟨R2⟩ + ⟨R3⟩ + ⟨C1⟩ + ⟨C2⟩ − ⟨C3⟩

where ⟨Ck⟩ is the expectation of the **product of the three individually- and compatibly-measured outcomes** in that context.

- **Noncontextual (classical) bound:** χ ≤ 4
- **Quantum prediction (any state):** χ = 6

**Compatible measurement gadget.** The three observables in a context commute, so they are measured jointly. Each observable's ±1 eigenvalue is read with an ancilla Hadamard-test parity gadget: `ancilla |0⟩ → H → controlled-(P₀ on q0, P₁ on q1) → H → measure`; outcome bit *b* gives eigenvalue (−1)ᵇ. Three observables → three ancillas → three bits/shot; the per-shot context correlator is (−1)^(b0+b1+b2). Because the observables commute, the gadgets commute and implement a genuine simultaneous (non-disturbing, in the ideal limit) measurement.

**Simulation validation (pre-lock, noiseless AerSimulator, 40 000 shots/context):**

| state | ⟨R1,R2,R3,C1,C2,C3⟩ | χ |
|-------|---------------------|---|
| \|00⟩ | [+1,+1,+1,+1,+1,−1] | **6.000** |
| \|++⟩ | [+1,+1,+1,+1,+1,−1] | **6.000** |
| Bell (entangled) | [+1,+1,+1,+1,+1,−1] | **6.000** |

χ = 6 for all three states — maximal quantum value, state-independence confirmed.

## 4. Execution plan

- **Backend:** IBM open-plan hardware (prefer `ibm_fez`, else min pending-jobs).
- **Circuits:** 6 contexts × 3 states = **18 circuits**, each 5 qubits (2 data + 3 ancilla), 3 clbits.
- **Shots:** 1000 per context (18 000 total) — sized to remaining open-plan budget (~a few seconds).
- **Mode:** Batch (open plan forbids Session). **Channel:** `ibm_quantum_platform`.
- **Circuits transpiled** to backend ISA (optimization_level=1) before submission.

## 5. Outcome criteria (fixed in advance — honest, symmetric)

Reported **per state** and aggregated:

| Verdict | Condition |
|---------|-----------|
| **CONTEXTUALITY (state-independent, under assumptions)** | χ > 4 and χ − 4 > 3σ for **every** state tested |
| **CONTEXTUALITY (state-dependent)** | χ > 4 (3σ) for some but not all states |
| **INCONCLUSIVE / HOLD** | χ > 4 but not 3σ-significant |
| **NO VIOLATION** | χ ≤ 4 |

The measured hardware χ for each state is reported **exactly as observed**. No re-runs to chase a preferred number.

## 6. Honesty boundary (non-negotiable — carried into every artifact)

- **Compatibility / non-disturbance loophole OPEN:** the ancilla parity gadgets are not perfectly non-disturbing on real hardware; a determined noncontextual modeller can attribute χ > 4 to measurement disturbance / finite-precision compatibility.
- **Detection / fair-sampling assumption required:** imperfect readout.
- **Single device**, no device-independence is claimed. **Not** certified randomness.
- **State-independence is asserted from theory and *demonstrated* across the states actually run** — not proven for literally all states.
- **Only defensible claim:** *"Observed Peres–Mermin state-independent contextuality violation (χ > 4) on quantum hardware across multiple input states, under compatibility + detection trust assumptions, cryptographically bound into the authorization record."*

### 6a. Disclosed pre-execution harness facts
- Proven WITNESS/BELLWETHER/CHRONO harness fixes are baked in: FIX-1 (backend via min pending_jobs), FIX-2 (transpile to ISA), FIX-3 (robust token loader). No physics impact.
- AerSimulator confirms the exact extraction path and χ = 6 for all three states. Hardware path (SamplerV2, Batch) is identical to prior validated experiments.

## 7. ProofRecord construction (`bellwether-proofrecord-3.0`)

```
raw_counts_hash  = H( canonical(counts_by_state_and_context) )
calibration_hash = H( canonical(calibration_snapshot) )
witness_hash     = H( canonical(contextuality_witness) )   # contains χ per state + verdicts
context_nonce    = H( lp(raw_counts_hash) || lp(job_id) || lp(calibration_hash) || lp(witness_hash) )
record_hash      = H( canonical(all fields except record_hash) )
```

Tampering with any measured χ breaks `context_nonce`; any covered-field edit breaks `record_hash`. Verified by 10/10 pre-lock mock tests (tamper-evidence over both counts and witness) and by the independent `verify.py`.

## 8. Commercial purpose & strategic value (Covenant requirement)

**IP thesis.** BELLWETHER-3 extends the ExecutionProof patent family with a **contextuality-based, state-independent authorization primitive**: a ProofRecord whose physical witness (a) is grounded in the resource that provably powers quantum computational advantage, and (b) certifies **robustness to the input state** — the authorization holds regardless of what preparation an adversary supplies. This is a materially different and broader claim surface than a Bell/GHZ witness (which is entanglement- and preparation-specific).

**Candidate RF-100 use.** *State-robust hardware authorization* — an ExecutionProof seed whose validity does not depend on trusting the preparation stage, only the (disclosed) compatibility/detection assumptions. Natural fit for supply-chain / firmware-attestation contexts where the prepared state cannot be fully trusted.

**Portfolio position.** With BELLWETHER (nonlocality: bipartite → multipartite), CHRONO (temporal), and now BELLWETHER-3 (contextuality), RF's ExecutionProof program spans **the three canonical families of quantum nonclassicality** — a coherent, defensible, and unusually broad experimental IP base built entirely on preregistered, independently-verifiable hardware runs. This breadth is itself a strategic moat: it is the difference between "a clever nonce" and "a systematic physical theory of authorization."

## 9. IP gate

BELLWETHER-3 is **almost certainly new patentable matter** (contextuality-based, state-independent authorization has, to our knowledge, no prior art). Per the Covenant it is held **local-only** (no GitHub / Zenodo / LinkedIn / RF-100 disclosure) until Derek makes the **file-first** determination. Execution is **not** disclosure; running the job and fetching results is permitted.

---

*To God be the glory. Proof Before Power. Verification Before Execution.*
