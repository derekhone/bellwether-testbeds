> **Repository Role:** Preregistered Experiment Series — Bell-Violation Entropy Witness (BELLWETHER) · Part of the [Remnant Fieldworks](https://remnantfieldworks.com) research and product ecosystem

**Where this fits:** This repository is part of the Remnant Fieldworks quantum witness research program — a high-adversity test environment for provenance and execution integrity that informs the [ExecutionProof](https://executionproof.io) governance architecture. The quantum series tests whether nonclassical entropy sources, Bell-inequality violations, and tamper-evident records can serve as authorization evidence components in ProofRecords. BELLWETHER binds an independently-verifiable CHSH Bell-violation entropy witness into an authorization ProofRecord.

---

# BELLWETHER Testbeds — Quantum Nonclassicality Witnesses Bound into Authorization Records

**Remnant Fieldworks Inc. — ExecutionProof Research Program**

The BELLWETHER series binds an independently-verifiable **quantum nonclassicality witness** into an
authorization nonce / ProofRecord, executed on IBM Quantum hardware under a strict
**preregistration-first** protocol (SHA-256 MANIFEST locked before any hardware submission).

Each experiment advances the *resource* being witnessed — moving from bipartite nonlocality, to
genuine multipartite entanglement, to state-independent contextuality.

## Series index

| Experiment | Witness | Resource | Bounds | Measured | Backend / Job | Verdict |
|------------|---------|----------|--------|----------|---------------|---------|
| **BELLWETHER-1** (root) | CHSH Bell inequality | Bipartite nonlocality | classical ≤2, quantum 2√2 | **S = 2.514** | ibm_fez / d9dje2cjeosc73fhm230 | ✅ PASS |
| **BELLWETHER-2** (`bellwether-2/`) | Mermin-3 (3-qubit GHZ) | Genuine multipartite entanglement | classical ≤2, quantum 4 | **\|M\| = 3.423** | ibm_fez / d9dno91htsac739da4d0 | ✅ PASS |
| **BELLWETHER-3** (`bellwether-3/`) | Peres–Mermin magic square | State-independent contextuality | noncontextual ≤4, quantum 6 | **χ = 5.27–5.38** (3 states) | ibm_fez / d9do1s1htsac739dahpg | ✅ PASS |

### Defensive-publication DOIs (Zenodo, published 2026-07-18)
| Experiment | DOI (version) | Concept DOI | Record |
|------------|---------------|-------------|--------|
| BELLWETHER-1 | 10.5281/zenodo.21430442 | 10.5281/zenodo.21430441 | https://zenodo.org/records/21430442 |
| BELLWETHER-2 | 10.5281/zenodo.21430446 | 10.5281/zenodo.21430445 | https://zenodo.org/records/21430446 |
| BELLWETHER-3 | 10.5281/zenodo.21430451 | 10.5281/zenodo.21430450 | https://zenodo.org/records/21430451 |
| CHRONO-1 | 10.5281/zenodo.21430455 | 10.5281/zenodo.21430454 | https://zenodo.org/records/21430455 |

These are **defensive publications**: they establish public, timestamped prior art (protecting freedom
to operate) while the core RF classical governance/cryptographic/authorization IP is already protected
by filed USPTO provisionals and the nonprovisional parent. See each experiment's report for details.

A companion series, **CHRONO** (Leggett–Garg temporal witness, K3 = 1.450), lives in the separate
`chrono-testbeds` repository. Together these span all three canonical nonclassicality families —
**nonlocality** (BELLWETHER-1/2), **temporal** (CHRONO-1), and **contextuality** (BELLWETHER-3).

## Honesty boundary (applies to the whole series)
These are **device-dependent** witnesses on co-located superconducting qubits. Locality, detection,
and (for BELLWETHER-3) compatibility/non-disturbance loopholes remain **OPEN**. Results are **NOT
loophole-free** and **NOT device-independent certified randomness**. Every claim applies only within
the tested circuit model, backend, qubits, calibration snapshot, and shot counts. State-independence
in BELLWETHER-3 is **demonstrated across the states run**, not proven for all states.

## Provenance & verification
- Each experiment preregisters a `MANIFEST.sha256` lock **before** hardware submission.
- Raw counts, calibration snapshot, and job metadata are committed under `results/raw/`.
- Run `python3 <experiment>/src/verify.py` to independently recompute the witness value and validate
  the `record_hash` and nonce from the raw counts.

## License
CC BY 4.0 — see [LICENSE](LICENSE) for the full terms already identified here. Existing file-specific and third-party notices remain applicable; this addition does not narrow previous grants or imply a production-backend license.

---
To God be the glory. **Proof Before Power. Verification Before Execution.**
