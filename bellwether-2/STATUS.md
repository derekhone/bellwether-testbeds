# BELLWETHER-2 — Status

**Experiment:** 3-qubit Mermin inequality (genuine multipartite entanglement) witness bound into ProofRecord.
**Series:** BELLWETHER (spatial nonclassicality) — advancement from BELLWETHER-1 bipartite to multipartite.

## State
- Design + harness: COMPLETE
- Mock tests: 10/10 PASS
- Simulation (AerSimulator, noiseless): |M| = 4.0 (classical bound |M|≤2 violated maximally)
- Preregistration: LOCKED (MANIFEST.sha256)
- Hardware job: see results/SUBMITTED_JOB_ID.txt once submitted
- IP gate: LOCAL-ONLY. No GitHub / Zenodo / LinkedIn / RF-100 until Derek's file-first determination.

## Finalize when job is DONE
    cd /home/ubuntu/bellwether-testbeds/bellwether-2
    python3 src/fetch_result.py
    python3 src/verify.py

## Honesty boundary
Device-dependent witness on co-located qubits. Locality loophole OPEN; detection loophole OPEN.
NOT loophole-free; NOT device-independent certified randomness.
