"""
tamper_detection_test.py
Proves the audit trail's hash-chaining actually works: deliberately
modifies a stored record directly via SQL (simulating an attacker or
insider with database access), then runs verify_chain_integrity() to
confirm the tampering is detected.
"""

import sys
import os
import sqlite3
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pattern-auditor"))
from action_store import DB_PATH, verify_chain_integrity


def tamper_with_a_record():
    """Directly modifies a stored record's final_decision to 'auto_approve',
    simulating an attacker altering history to hide that an action was
    actually blocked or escalated."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, raw_record FROM action_history ORDER BY id ASC LIMIT 1")
    row = cursor.fetchone()
    if row is None:
        print("[!] No records to tamper with. Run a test script first to populate the database.")
        conn.close()
        return None

    record_id, raw_record = row
    record = json.loads(raw_record)
    original_decision = record["final_decision"]

    # Force a guaranteed content change regardless of the original value --
    # add a field that could not possibly have existed when the hash was
    # originally computed, simulating an attacker altering the record.
    record["final_decision"] = "auto_approve"
    record["tampered_by_test"] = True

    cursor.execute(
        "UPDATE action_history SET raw_record = ?, final_decision = ? WHERE id = ?",
        (json.dumps(record, sort_keys=True), "auto_approve", record_id),
    )
    conn.commit()
    conn.close()

    print(f"[*] Tampered with record id={record_id}: changed final_decision "
          f"from '{original_decision}' to 'auto_approve' and added a marker field "
          f"(note: record_hash was NOT recomputed)")
    return record_id


if __name__ == "__main__":
    print("=== Step 1: Verify chain BEFORE tampering ===")
    before = verify_chain_integrity()
    print(json.dumps(before, indent=2))

    print("\n=== Step 2: Tamper with a record directly via SQL ===")
    tampered_id = tamper_with_a_record()

    if tampered_id is not None:
        print("\n=== Step 3: Verify chain AFTER tampering ===")
        after = verify_chain_integrity()
        print(json.dumps(after, indent=2))

        if not after["chain_intact"] and after.get("broken_at_id") == tampered_id:
            print(f"\n[+] SUCCESS: Tampering was correctly detected at record id={tampered_id}")
        else:
            print("\n[!] Tampering was NOT correctly detected -- integrity check has a gap")