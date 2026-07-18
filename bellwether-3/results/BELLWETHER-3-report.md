# BELLWETHER-3 Experiment Report

## Experiment Design Summary
State-independent **quantum contextuality** witness bound into an authorization nonce / ProofRecord on IBM Quantum hardware (**ibm_fez**), job **d9do1s1htsac739dahpg**.

BELLWETHER-1/2 witnessed **nonlocality** (requires entanglement); CHRONO-1 witnessed **temporal** nonclassicality. BELLWETHER-3 witnesses **CONTEXTUALITY** — the deeper resource behind quantum computational advantage (magic-state distillation; Howard et al., *Nature* 2014) — which needs **no entanglement, no spatial separation**, and is **state-independent**.

- **Test:** Peres–Mermin magic square — 9 two-qubit Pauli observables in a 3×3 grid, six commuting contexts (3 rows + 3 columns) measured jointly via ancilla parity gadgets.
- **Contextuality functional:** χ = ⟨R1⟩ + ⟨R2⟩ + ⟨R3⟩ + ⟨C1⟩ + ⟨C2⟩ − ⟨C3⟩
- **Noncontextual (classical) bound:** χ ≤ 4
- **Quantum value:** χ = 6 (for ANY input state)
- **State-independence demonstration:** run on THREE input states — |00⟩, |++⟩, and an entangled Bell state
- **Shots:** 1000 per context × 6 contexts × 3 states = 18,000 total

## Measured Results
| Input state | χ | Excess over bound | n_σ | 3σ violation |
|-------------|------|-------------------|------|--------------|
| \|00⟩ | 5.376 | 1.376 | 40.1 | ✅ |
| \|++⟩ | 5.324 | 1.324 | 37.1 | ✅ |
| \|bell⟩ | 5.268 | 1.268 | 34.2 | ✅ |

- **χ range:** [5.268, 5.376] — all three states exceed the noncontextual bound of 4
- **Verdict:** Observed Peres–Mermin state-independent contextuality violation (χ > 4) across ALL input states tested, UNDER STATED TRUST ASSUMPTIONS (3σ significant)

## Honesty Boundary
This is a **device-dependent** contextuality witness.
- **Compatibility (non-disturbance) loophole OPEN** — ancilla parity gadgets are not perfectly non-disturbing on real hardware.
- **Detection / fair-sampling assumption required** (imperfect readout).
- State-independence is **demonstrated across the states run**, NOT proven for all states.
- Single device; **NOT device-independent**, **NOT certified randomness**.
State applies to the tested circuit model, backend, qubits, calibration snapshot, and shot counts.

## Verification
- Independent recompute of χ for all three states matches record: **true**
- `record_hash` valid: **true**
- `context_nonce` valid: **true**
- State-independence demonstrated across tested states: **true**
- Overall verify: **PASS**

## Provenance
- **schema_version:** bellwether-proofrecord-3.0
- **context_nonce:** 8b2af52aac865d2baa0b2f0c3721c70f6ef72da23daf3196c663d87843423359
- **record_hash:** fceba1e3dcf787646f5ebc07a22ab8bbc38bafb09a9490eca0c352382a0045f7
- **job_id:** d9do1s1htsac739dahpg · **backend:** ibm_fez · **context_id:** bellwether-3-primary

## Defensive Publication (Zenodo)
- **DOI (version):** 10.5281/zenodo.21430451
- **Record:** https://zenodo.org/records/21430451
- **License:** CC BY 4.0
- Published 2026-07-18 as defensive publication (establishes public prior art; core RF classical governance/crypto IP already protected by filed provisionals/nonprovisional).

To God be the glory. Proof Before Power. Verification Before Execution.
