"""
action_store.py
Stores every action that reaches a final decision (from the Governor/OPA)
into a local SQLite database. This history is what the Pattern Auditor
analyzes to detect cumulative-risk patterns -- actions that individually
passed but collectively resemble something that should have been blocked.
"""

import sqlite3
import json
import os
from datetime import datetime, timezone
from action_classifier import classify_action

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "action_history.db")


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
            raw_record TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def store_action(audit_record: dict):
    """Persists a single Governor audit record, including its normalized
    category, into the action history table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    action = audit_record["proposed_action"]
    category = classify_action(action)

    cursor.execute("""
        INSERT INTO action_history
        (timestamp, action_type, normalized_category, target, scope, reversible, final_decision, raw_record)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        audit_record["timestamp"],
        action["action_type"],
        category,
        action["target"],
        action["scope"],
        int(action["reversible"]),
        audit_record["final_decision"],
        json.dumps(audit_record),
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


if __name__ == "__main__":
    init_db()
    print(f"[+] Initialized database at {DB_PATH}")