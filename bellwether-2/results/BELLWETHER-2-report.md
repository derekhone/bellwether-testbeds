# BELLWETHER-2 Experiment Report

## Experiment Design Summary
Multipartite entanglement witness bound into an authorization nonce / ProofRecord on IBM Quantum hardware (**ibm_fez**), job **d9dno91htsac739da4d0**.

This is a genuine advancement from the bipartite CHSH test of BELLWETHER-1 to the **multipartite** regime: a 3-qubit GHZ state |GHZ⟩ = (|000⟩ + |111⟩)/√2 witnessed by the **Mermin-3** inequality

    M = ⟨XYY⟩ + ⟨YXY⟩ + ⟨YYX⟩ − ⟨XXX⟩

- **Classical (local-hidden-variable) bound:** |M| ≤ 2
- **Quantum maximum:** |M| = 4
- **Shots:** 2000 per setting × 4 settings = 8000 total
- **Authorization angle:** a multipartite witness models multi-authority authorization — 3+ parties must jointly agree, and the correlation cannot be reproduced by any pair acting alone.

## Measured Results
- **Measured Mermin value:** M = −3.4230  (|M| = 3.423)
- **Component correlators:** ⟨XYY⟩=−0.888, ⟨YXY⟩=−0.824, ⟨YYX⟩=−0.831, ⟨XXX⟩=+0.880
- **Excess over classical bound:** 1.423
- **Statistical significance:** n_σ ≈ 61.6 (σ_M ≈ 0.0231)
- **Verdict:** Observed genuine-multipartite Mermin violation UNDER STATED TRUST ASSUMPTIONS (3σ significant)

## Honesty Boundary
This is a **device-dependent** multipartite-entanglement witness. Locality and detection loopholes remain **OPEN** on co-located superconducting qubits. The sign of M reflects the measured GHZ-phase convention; the physical claim is on the **magnitude** |M| = 3.423 > 2. This result is **NOT loophole-free** and **NOT device-independent certified randomness**. State applies to the tested circuit model, backend, qubits, calibration snapshot, and shot counts.

## Verification
- Independent recompute of M from raw counts matches record: **true**
- `record_hash` valid: **true**
- `mermin_nonce` valid: **true**
- Overall verify: **PASS**

## Provenance
- **schema_version:** bellwether-proofrecord-2.0
- **mermin_nonce:** 20f8a53a7dac75875ece12131a2dbc7c431ed5a1f48cc1e01d34b996c10832ac
- **record_hash:** b69903f1e48342fb68ff2f832c1be53e3e1d4a2a8859aa1c4db66e025fa0fbcd
- **job_id:** d9dno91htsac739da4d0 · **backend:** ibm_fez · **context_id:** bellwether-2-primary

To God be the glory. Proof Before Power. Verification Before Execution.
