"""
BELLWETHER-3 — standalone result fetcher.

Retrieves the finished hardware job BY ID from IBM (results persist server-side)
and performs the same post-execution steps as submit_job.py: regroup counts per
state/context, compute chi per state, build the contextuality witness +
ProofRecord, and write all artifacts under results/. Safe in a fresh session.

Usage: python3 src/fetch_result.py [JOB_ID]
Default JOB_ID is read from results/raw/job_meta.json or results/SUBMITTED_JOB_ID.txt.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import peres_mermin as pm
import submit_job as sj  # reuse STATES, SHOTS, _extract_counts, _finalize

RESULTS = sj.RESULTS
RAW = sj.RAW


def _default_job_id() -> str:
    meta = os.path.join(RAW, "job_meta.json")
    if os.path.exists(meta):
        try:
            return json.load(open(meta)).get("job_id", "")
        except Exception:
            pass
    jf = os.path.join(RESULTS, "SUBMITTED_JOB_ID.txt")
    if os.path.exists(jf):
        return open(jf).read().strip()
    return ""


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService

    job_id = sys.argv[1] if len(sys.argv) > 1 else _default_job_id()
    if not job_id:
        print("[fetch] no job id known; pass JOB_ID on the command line.")
        return 2
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=sj.load_token())
    job = svc.job(job_id)
    status = str(job.status())
    print(f"[fetch] job {job_id} status={status}")
    if status not in ("DONE", "JobStatus.DONE"):
        print("[fetch] job not finished yet; re-run when DONE.")
        return 2

    backend = job.backend()
    backend_name = backend.name if hasattr(backend, "name") else str(backend)
    result = job.result()

    # Rebuild the same (state, context) index used at submission.
    _, index = pm.build_all_circuits(sj.STATES)
    counts_flat = [sj._extract_counts(result[i]) for i in range(len(result))]

    cal = {"backend": backend_name}
    try:
        props = backend.properties()
        cal["last_update_date"] = str(getattr(props, "last_update_date", ""))
    except Exception as e:
        cal["properties_error"] = repr(e)[:200]

    sj._finalize(counts_flat, index, job_id, backend_name, cal)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
