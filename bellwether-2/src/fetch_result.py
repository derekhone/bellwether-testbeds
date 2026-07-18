"""
BELLWETHER-2 — standalone result fetcher.

Retrieves the finished hardware job BY ID from IBM (results persist server-side)
and performs the same post-execution steps as submit_job.py: compute M, build
the multipartite witness + ProofRecord, and write all artifacts under results/.
Safe to run in a fresh session.

Usage: python3 src/fetch_result.py [JOB_ID]
The default JOB_ID is read from results/raw/job_meta.json or results/SUBMITTED_JOB_ID.txt.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import mermin
import multipartite_witness as mw
import proofrecord as pr

RESULTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
RAW = os.path.join(RESULTS, "raw")
SHOTS = 2000
DEFAULT_JOB_ID = ""


def load_token() -> str:
    d = json.load(open("/home/ubuntu/.config/abacusai_auth_secrets.json"))
    for key in ("ibm quantum", "witness1_ibmq", "ibm_quantum"):
        if key in d:
            return d[key]["secrets"]["api_token"]["value"]
    raise RuntimeError("no IBM Quantum token key found")


def _default_job_id() -> str:
    meta = os.path.join(RAW, "job_meta.json")
    if os.path.exists(meta):
        try:
            return json.load(open(meta)).get("job_id", DEFAULT_JOB_ID)
        except Exception:
            pass
    jf = os.path.join(RESULTS, "SUBMITTED_JOB_ID.txt")
    if os.path.exists(jf):
        return open(jf).read().strip()
    return DEFAULT_JOB_ID


def _extract_counts(pub_result):
    data = pub_result.data
    keys = list(data.keys()) if hasattr(data, "keys") \
        else [k for k in dir(data) if not k.startswith("_")]
    creg = keys[0]
    return data[creg].get_counts() if hasattr(data, "__getitem__") \
        else getattr(data, creg).get_counts()


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService

    job_id = sys.argv[1] if len(sys.argv) > 1 else _default_job_id()
    if not job_id:
        print("[fetch] no job id known; pass JOB_ID on the command line.")
        return 2
    os.makedirs(RAW, exist_ok=True)
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=load_token())
    job = svc.job(job_id)
    status = str(job.status())
    print(f"[fetch] job {job_id} status={status}")
    if status not in ("DONE", "JobStatus.DONE"):
        print("[fetch] job not finished yet; re-run when DONE.")
        return 2

    backend = job.backend()
    backend_name = backend.name if hasattr(backend, "name") else str(backend)
    result = job.result()
    counts_by_setting = [_extract_counts(result[i]) for i in range(len(result))]
    for i, c in enumerate(counts_by_setting):
        print(f"  {mermin.SETTINGS[i]}: {c}")

    M, E = mermin.compute_M(counts_by_setting)
    sigma = mermin.shot_noise_sigma_M(E, SHOTS)
    witness = mw.build_witness(M, E, SHOTS, sigma)
    print(f"[fetch] M = {M:.4f}  violation={witness['violation']} "
          f"3sigma={witness['significant_violation_3sigma']}")

    cal = {"backend": backend_name}
    try:
        props = backend.properties()
        cal["last_update_date"] = str(getattr(props, "last_update_date", ""))
    except Exception as e:
        cal["properties_error"] = repr(e)[:200]

    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record = pr.build_proofrecord(counts_by_setting, job_id, backend_name,
                                  "open-instance", cal, witness,
                                  "bellwether-2-primary", ts)

    json.dump({"counts_by_setting": counts_by_setting,
               "settings_order": mermin.SETTINGS},
              open(os.path.join(RAW, "raw_counts.json"), "w"), indent=2)
    json.dump({"job_id": job_id, "backend": backend_name,
               "shots_per_setting": SHOTS, "timestamp_utc": ts},
              open(os.path.join(RAW, "job_meta.json"), "w"), indent=2)
    json.dump(cal, open(os.path.join(RAW, "calibration_snapshot.json"), "w"), indent=2)
    json.dump(record, open(os.path.join(RESULTS, "proofrecord.json"), "w"), indent=2)
    json.dump({"M": M, "E_values": E, "witness": witness},
              open(os.path.join(RESULTS, "BELLWETHER-2-result.json"), "w"), indent=2)
    print("[fetch] artifacts written under results/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
