# BELLWETHER-2 — Preregistration

**Series:** BELLWETHER (spatial nonclassicality witness)  
**Experiment ID:** BELLWETHER-2  
**Owner:** Remnant Fieldworks Inc. (Derek Adam Hone)  
**Status at lock:** design + harness complete, validated in simulation, hardware job pending  
**Governing framework:** RF Experiment–Pilot–IP Covenant (preregistration-first; honest outcomes; claims narrower than evidence; file-first / publish-after for new matter)

---

## 1. One-sentence statement

We measure the **3-qubit Mermin inequality** (genuine multipartite entanglement) on a GHZ state and **cryptographically bind the measured M statistic into an authorization ProofRecord** as a *multipartite* spatial nonclassicality witness — a certificate that three independent parties must jointly agree.

## 2. Why this is new (advancement over BELLWETHER-1)

| Series | State | Test | Witnessed |
|--------|-------|------|-----------|
| BELLWETHER-1 | 2-qubit Bell+ | CHSH (S>2) | **bipartite** entanglement (Alice + Bob) |
| **BELLWETHER-2** | 3-qubit GHZ | Mermin-3 (\|M\|>2) | **genuine multipartite** entanglement (Alice + Bob + Charlie) |

**Key advancement:** Mermin violations grow exponentially with # qubits and certify **genuine** (not just pairwise) multipartite entanglement. BELLWETHER-1 tested 2-party entanglement; BELLWETHER-2 tests 3-party *joint* nonclassicality.

**Authorization angle:** multipartite witness models **multi-authority authorization** — multiple independent parties must jointly agree. The ProofRecord binds physical evidence that the authorization value cannot be replicated by any pair acting alone.

## 3. Physics and design

**State:** 3-qubit GHZ state  
|GHZ⟩ = (|000⟩ + |111⟩)/√2

**Test:** Mermin-Klyshko inequality for 3 qubits:

    M = ⟨A₁B₁C₁⟩ + ⟨A₁B₂C₂⟩ + ⟨A₂B₁C₂⟩ − ⟨A₂B₂C₁⟩

where A₁,A₂ are Alice's measurement choices (X,Y), B₁,B₂ are Bob's (Y,X), C₁,C₂ are Charlie's (Y,X).

Four measurement circuits (in operator notation):
- **XYY**: X⊗Y⊗Y
- **YXY**: Y⊗X⊗Y  
- **YYX**: Y⊗Y⊗X
- **XXX**: X⊗X⊗X

Each 3-bit outcome maps to a parity: (-1)^(popcount). Expectation value = shot-average of parities.

**Bounds:**
- **Classical (local-realistic) bound:** |M| ≤ 2
- **Quantum (GHZ) prediction:** |M| = 4

**Simulation validation (pre-lock, noiseless AerSimulator, 200k shots/setting):**  
E = [−1.000, −1.000, −1.000, +1.000] → **M = −4.000**  
(Sign is a basis/phase convention; the violation is |M| = 4 >> 2, confirming maximal quantum value.)

## 4. Execution plan

- **Backend:** IBM open-plan hardware (prefer `ibm_fez`, else min pending-jobs).
- **Shots:** 2000 per setting × 4 = **8000 shots total** (~a few seconds of QPU time; sized to remaining open-plan budget).
- **Mode:** Batch (open plan forbids Session). **Channel:** `ibm_quantum_platform`.
- **Circuits transpiled** to backend ISA (optimization_level=1) before submission.

## 5. Outcome criteria (fixed in advance — honest, symmetric)

| Verdict | Condition |
|---------|-----------|
| **VIOLATION (genuine multipartite entanglement, under assumptions)** | \|M\| > 2 and \|M\| − 2 > 3σ |
| **INCONCLUSIVE / HOLD** | \|M\| > 2 but not 3σ-significant |
| **NO VIOLATION** | \|M\| ≤ 2 |

The measured hardware M will be reported **exactly as observed**, whichever bin it lands in. No re-runs to chase a preferred number.

## 6. Honesty boundary (non-negotiable — carried into every artifact)

- **Locality loophole OPEN:** Co-located qubits on a single chip can in principle communicate classically. A determined local-realist can attribute any |M| > 2 to such signaling.
- **Detection loophole OPEN:** Imperfect readout means not all events are detected. Fair-sampling assumption required.
- This is therefore a **Mermin violation UNDER STATED TRUST ASSUMPTIONS**, **not** loophole-free, and **not** device-independent certified randomness.
- **Single device**, no device-independence is claimed.
- **Only defensible claim:** *"Observed 3-qubit Mermin inequality violation (genuine multipartite entanglement) on quantum hardware, under locality + detection trust assumptions, cryptographically bound into the authorization record."*

### 6a. Disclosed pre-execution harness facts
- The proven WITNESS/BELLWETHER-1/CHRONO harness fixes are baked in: FIX-1 (robust backend selection via min pending_jobs), FIX-2 (transpile to ISA before submission), FIX-3 (robust token loader). No physics impact.
- Simulator (`AerSimulator`) confirms the exact extraction path and |M| = 4. Hardware path (SamplerV2, Batch) is identical to prior validated experiments.

## 7. ProofRecord construction (`bellwether-proofrecord-2.0`)

```
raw_counts_hash      = H( canonical(counts_by_setting) )
calibration_hash     = H( canonical(calibration_snapshot) )
witness_hash         = H( canonical(multipartite_witness) )  # contains M, E_values, bounds
mermin_nonce         = H( lp(raw_counts_hash) || lp(job_id) || lp(calibration_hash) || lp(witness_hash) )
record_hash          = H( canonical(all fields except record_hash) )
```

Tampering with the measured statistic breaks `mermin_nonce`; any covered-field edit breaks `record_hash`. Verified by 10/10 pre-lock mock tests (tamper-evidence over both counts and witness) and by the independent `verify.py`.

## 8. Commercial purpose (Covenant requirement)

BELLWETHER-2 extends the ExecutionProof patent family with a **multipartite** entropy/authorization primitive: a ProofRecord whose witness certifies that **three or more independent parties must jointly agree** — cannot be replicated by any pair acting alone. Candidate RF-100 use: **multi-authority / multi-signature authorization** (e.g., 3-of-3 board approval, nuclear two-person rule extended to N parties). Publication is gated pending the file-first IP determination (§9).

## 9. IP gate

BELLWETHER-2 is **almost certainly new patentable matter**. Per the Covenant it is held **local-only** (no GitHub / Zenodo / LinkedIn / RF-100 disclosure) until Derek makes the **file-first** determination. Execution is **not** disclosure; running the job and fetching results is permitted.

---

*To God be the glory. Proof Before Power. Verification Before Execution.*
