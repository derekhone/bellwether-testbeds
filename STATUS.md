# BELLWETHER-1 — STATUS

- **State:** designed, built, mock-tested (8/8 PASS), local-sim validated (S≈2.83), preregistration LOCKED. Hardware job SUBMITTED + QUEUED.
- **Job ID:** d9dje2cjeosc73fhm230  (backend ibm_fez, open plan)
- **Queue:** long (open-plan fair-share deprioritization; pending count rising). Result persists server-side at IBM.
- **To finalize when the job is DONE (one command):**
  ```
  cd /home/ubuntu/bellwether-testbeds && python3 src/fetch_result.py
  python3 src/verify.py    # independent recompute of S + provenance
  ```
- **IP GATE:** results are HELD — do NOT publish to GitHub/Zenodo/LinkedIn/RF-100 until Derek makes the file-first determination (likely NEW MATTER).
