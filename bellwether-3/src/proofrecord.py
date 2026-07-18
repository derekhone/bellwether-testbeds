"""
BELLWETHER-3 — ProofRecord with a bound state-independent contextuality witness.

schema_version: bellwether-proofrecord-3.0

Novelty vs. BELLWETHER-1/2: the record carries a `contextuality_witness` block
(the Peres–Mermin chi statistic across one or more input states + violation
verdict) AND a `context_nonce` whose preimage includes that witness. Tampering
with the witness breaks the nonce; the record_hash covers the whole record. The
bound quantity is a STATE-INDEPENDENT contextuality certificate — an
authorization primitive robust to the input-state (preparation) an adversary
supplies.

Provenance chain (all SHA-256, length-prefixed canonical JSON):
    raw_counts_hash    = H( canonical(counts_by_state_and_context) )
    calibration_hash   = H( canonical(calibration_snapshot) )
    witness_hash       = H( canonical(contextuality_witness) )
    context_nonce      = H( lp(raw_counts_hash) || lp(job_id) ||
                            lp(calibration_hash) || lp(witness_hash) )
    record_hash        = H( canonical(all record fields except record_hash) )
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

SCHEMA_VERSION = "bellwether-proofrecord-3.0"


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_hex(obj: Any) -> str:
    return _sha256(canonical_json(obj))


def lp(b: bytes) -> bytes:
    """Length-prefix with 8-byte big-endian length (anti boundary-collision)."""
    return len(b).to_bytes(8, "big") + b


def compute_context_nonce(raw_counts_hash: str, job_id: str,
                          calibration_hash: str, witness_hash: str) -> str:
    h = hashlib.sha256()
    for part in (raw_counts_hash, job_id, calibration_hash, witness_hash):
        h.update(lp(part.encode("utf-8")))
    return h.hexdigest()


def build_proofrecord(counts_payload, job_id: str, backend: str,
                      provider_instance: str, calibration_snapshot: Dict,
                      contextuality_witness: Dict, context_id: str,
                      timestamp_utc: str) -> Dict:
    raw_counts_hash = sha256_hex(counts_payload)
    calibration_hash = sha256_hex(calibration_snapshot)
    witness_hash = sha256_hex(contextuality_witness)
    context_nonce = compute_context_nonce(raw_counts_hash, job_id,
                                          calibration_hash, witness_hash)
    record = {
        "schema_version": SCHEMA_VERSION,
        "context_nonce": context_nonce,
        "contextuality_witness": contextuality_witness,
        "raw_counts_hash": raw_counts_hash,
        "calibration_hash": calibration_hash,
        "witness_hash": witness_hash,
        "job_id": job_id,
        "backend": backend,
        "provider_instance": provider_instance,
        "context_id": context_id,
        "timestamp_utc": timestamp_utc,
    }
    record["record_hash"] = _sha256(canonical_json(
        {k: v for k, v in record.items() if k != "record_hash"}))
    return record


def verify_record_hash(record: Dict) -> bool:
    expected = _sha256(canonical_json(
        {k: v for k, v in record.items() if k != "record_hash"}))
    return expected == record.get("record_hash")


def verify_context_nonce(record: Dict, counts_payload,
                         calibration_snapshot, contextuality_witness) -> bool:
    rc = sha256_hex(counts_payload)
    cal = sha256_hex(calibration_snapshot)
    wit = sha256_hex(contextuality_witness)
    if rc != record.get("raw_counts_hash"):
        return False
    if cal != record.get("calibration_hash"):
        return False
    if wit != record.get("witness_hash"):
        return False
    expect = compute_context_nonce(rc, record["job_id"], cal, wit)
    return expect == record.get("context_nonce")
