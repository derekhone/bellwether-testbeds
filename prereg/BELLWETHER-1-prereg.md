# BELLWETHER-1 — Preregistration

**Title:** A Bell-Inequality-Witnessed Authorization Nonce (CHSH entropy witness bound into a ProofRecord)
**Series:** BELLWETHER (new, independent — distinct from ARK, WITNESS, UIP)
**Prepared:** 2026-07-18 · Remnant Fieldworks Inc.
**Status:** LOCKED before QPU execution (MANIFEST.sha256)

---

## 1. Question

Can we run a **live CHSH Bell test on hardware**, obtain a genuine violation of the
classical bound (S > 2), and **cryptographically bind that S statistic into an
authorization nonce / ProofRecord** so that the record carries a *physical witness*
of the nonclassical correlation that produced it — with tamper-evidence over the
witness itself?

This is novel relative to prior RF work:
- **ARK** tested the authorization *boundary* (ALLOW/HOLD/DENY under attack).
- **WITNESS** *assumed* superposition supplied unpredictability and hashed the
  provenance chain (counts, job_id, calibration).
- **BELLWETHER** *witnesses the nonclassicality itself* (a Bell violation) and binds
  the witness statistic into the record — a new `entropy_witness` field and a
  `bell_nonce` whose preimage includes it.

## 2. Design (fixed before execution)

- State: |Phi+> = (|00> + |11>)/sqrt(2).
- Four CHSH settings at the maximal-violation angles:
  Alice a=0, a'=pi/2 ; Bob b=pi/4, b'=3pi/4.
- Observable at angle theta measured by RY(-theta) then Z-measurement, so
  E(alpha,beta) = cos(alpha - beta) for |Phi+>.
- S = E(a,b) - E(a,b') + E(a',b) + E(a',b').
- Shots: 1000 per setting (4000 total). Backend: ibm_fez preferred (Heron r2),
  else ibm_marrakesh / ibm_kingston. Batch mode, ISA-transpiled (opt level 1).

## 3. Preregistered outcome criteria (no post-hoc changes)

- **Statistical uncertainty:** sigma_S <= 2/sqrt(N_per_setting) (conservative).
- **PASS (violation):** S - 2 > 3 * sigma_S  → significant Bell violation on hardware.
- **INCONCLUSIVE:** 2 < S <= 2 + 3*sigma_S → violation not statistically significant.
- **FAIL (honest):** S <= 2 → no violation; reported as-is, no rescue, no rerun-to-win.
- Provenance: record_hash and bell_nonce must reverify from raw artifacts (verify.py).

Whatever S comes out, it is reported honestly. A null/failed violation is a valid,
publishable RF outcome (consistent with ARK-445 / ARK-455 precedent).

## 4. Entropy-witness honesty boundary (carried into every artifact)

The device-independent (DI) relation P_guess(S) <= 1/2(1 + sqrt(2 - S^2/4)) and
H_min = -log2(P_guess) are computed **for illustration only**. On a single
superconducting chip the **locality loophole** (co-located, jointly measured qubits)
and the **detection loophole** (imperfect readout, no fair-sampling certification)
are **open**. Therefore:

> The defensible claim is limited to: "We observed a CHSH value S > 2 — a Bell-
> inequality violation on hardware under stated trust assumptions — and bound that
> statistic into the authorization record." It is NOT device-independent certified
> randomness. The min-entropy figure is illustrative, flagged loopholes_open=True.

Claims are kept narrower than the evidence (RF doctrine).

## 5. Covenant justification (Experiment–Pilot–IP)

- **Commercial purpose / one-sentence hook:** gives security & compliance buyers a
  *physically-witnessed* entropy story for the ProofRecord ("Bell-violation-backed
  unpredictability, honestly bounded") — a differentiator no competitor offers.
- **RF-100 requirement:** entropy-source assurance / provenance conformance for a
  verification artifact.
- **Patent-family connection:** the construction "bind a live Bell-violation
  statistic into an authorization nonce with tamper-evidence over the witness" is
  plausibly **NEW MATTER** not supported by existing filings.

## 6. IP GATE (decided BEFORE any public disclosure)

Running and obtaining the result is **not** disclosure. Publication to GitHub /
Zenodo / LinkedIn / RF-100 is gated on Derek's determination:
1. Does BELLWETHER merely demonstrate an already-filed invention? → likely NO.
2. Does it reveal new matter (the Bell-witness binding)? → likely YES.
3. Is it supported by a pending application? → to confirm.
4. **File first, publish after** if new matter. Working example labeled as of the
   execution date; never implied to predate any filing.

## 7. Protocol

LOCK (this MANIFEST) → mock tests PASS → execute one QPU job → compute S →
build ProofRecord → write artifacts → HOLD publication pending IP gate.

**To God be the glory. Proof Before Power. Verification Before Execution.**
