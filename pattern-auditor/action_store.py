"""
action_store.py
Stores every action that reaches a final decision into a local SQLite
database, with HASH-CHAINING for audit trail integrity: each record's
hash incorporates the previous record's hash, so any tampering with a
past record is detectable (the chain breaks from that point forward).
This doesn't PREVENT tampering (SQLite has no built-in write protection),
but it makes tampering PROVABLE, which is the realistic bar for a
student-project audit trail.
"""

import sqlite3
import json
import os
import hashlib
from datetime import datetime, timezone
from action_classifier import classify_action

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "action_history.db")
GENESIS_HASH = "0" * 64  # the "previous hash" for the very first record


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            action_type TEXT NOT NULL,
            normalized_category TEXT NOT NULL,
            target TEXT NOT NULL,
            scope TEXT NOT NULL,
            reversible INTEGER NOT NULL,
            final_decision TEXT NOT NULL,
            raw_record TEXT NOT NULL,
            prev_hash TEXT NOT NULL,
            record_hash TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def _compute_hash(prev_hash: str, raw_record: str) -> str:
    """Computes a SHA-256 hash chaining this record to the previous one."""
    combined = f"{prev_hash}{raw_record}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


def _get_last_hash() -> str:
    """Returns the record_hash of the most recent entry, or GENESIS_HASH
    if the table is empty."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT record_hash FROM action_history ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else GENESIS_HASH


def store_action(audit_record: dict):
    """Persists a single Governor audit record, chained to the previous
    record's hash for tamper-evidence."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    action = audit_record["proposed_action"]
    category = classify_action(action)

    raw_record_json = json.dumps(audit_record, sort_keys=True)
    prev_hash = _get_last_hash()
    record_hash = _compute_hash(prev_hash, raw_record_json)

    cursor.execute("""
        INSERT INTO action_history
        (timestamp, action_type, normalized_category, target, scope, reversible,
         final_decision, raw_record, prev_hash, record_hash)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        audit_record["timestamp"],
        action["action_type"],
        category,
        action["target"],
        action["scope"],
        int(action["reversible"]),
        audit_record["final_decision"],
        raw_record_json,
        prev_hash,
        record_hash,
    ))
    conn.commit()
    conn.close()


def get_recent_actions(minutes: int = 10) -> list[dict]:
    """Returns all actions stored within the last N minutes, most recent last."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT raw_record, normalized_category FROM action_history ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    now = datetime.now(timezone.utc)
    recent = []
    for raw, category in rows:
        record = json.loads(raw)
        record["normalized_category"] = category
        ts = datetime.fromisoformat(record["timestamp"])
        if (now - ts).total_seconds() <= minutes * 60:
            recent.append(record)
    return recent


def verify_chain_integrity() -> dict:
    """
    Walks the ENTIRE audit trail and recomputes each record's hash from
    scratch, checking it against the stored hash and against the chain
    link to the previous record. Returns whether the chain is intact, and
    the first point of tampering if not.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, raw_record, prev_hash, record_hash FROM action_history ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()

    expected_prev_hash = GENESIS_HASH
    for row_id, raw_record, stored_prev_hash, stored_record_hash in rows:
        if stored_prev_hash != expected_prev_hash:
            return {
                "chain_intact": False,
                "broken_at_id": row_id,
                "reason": "prev_hash does not match the actual previous record's hash "
                          "-- a record may have been deleted, inserted, or reordered.",
            }

        recomputed_hash = _compute_hash(stored_prev_hash, raw_record)
        if recomputed_hash != stored_record_hash:
            return {
                "chain_intact": False,
                "broken_at_id": row_id,
                "reason": "record_hash does not match recomputed hash -- this record's "
                          "content was modified after it was originally stored.",
            }

        expected_prev_hash = stored_record_hash

    return {
        "chain_intact": True,
        "total_records_verified": len(rows),
    }


if __name__ == "__main__":
    init_db()
    print(f"[+] Initialized database at {DB_PATH}")

    result = verify_chain_integrity()
    print(json.dumps(result, indent=2))