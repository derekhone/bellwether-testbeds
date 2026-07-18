# BELLWETHER-3 — Status

**Experiment:** Peres–Mermin magic-square STATE-INDEPENDENT CONTEXTUALITY witness bound into ProofRecord.
**Series:** BELLWETHER (3rd in series; 4th RF quantum flagship overall).
**Resource jump:** from nonlocality (BELLWETHER-1/2) and temporal (CHRONO-1) to CONTEXTUALITY — no entanglement, no spatial separation, state-independent.

## State
- Design + harness: COMPLETE
- Mock tests: 10/10 PASS
- Simulation (AerSimulator, noiseless): chi = 6.000 for |00>, |++>, and Bell (state-independent). Noncontextual bound chi<=4; quantum value 6.
- Preregistration: LOCKED (MANIFEST.sha256)
- Hardware job: see results/SUBMITTED_JOB_ID.txt once submitted
- IP gate: LOCAL-ONLY. No GitHub / Zenodo / LinkedIn / RF-100 until Derek's file-first determination.

## Finalize when job is DONE
    cd /home/ubuntu/bellwether-testbeds/bellwether-3
    python3 src/fetch_result.py
    python3 src/verify.py

## Honesty boundary
Device-dependent contextuality witness. Compatibility (non-disturbance) loophole OPEN; detection/fair-sampling assumption required.
State-independence demonstrated across states run, not proven for all states. NOT loophole-free; NOT device-independent certified randomness.
