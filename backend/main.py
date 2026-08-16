"""
main.py
FastAPI backend tying together the full ThresholdGuard pipeline:
Blue Agent (detection) -> Governor (LLM advisory + OPA binding decision)
-> Pattern Auditor (cumulative risk check).

Exposes REST endpoints so a frontend dashboard (or any client) can trigger
an investigation and view the audit trail, without needing to run the
individual module scripts manually.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "blue-agent"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "governor"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pattern-auditor"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "red-agent"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from blue_agent import run_blue_agent_investigation
from governor import evaluate_action
from action_store import init_db, store_action, get_recent_actions
from pattern_auditor import audit_recent_actions

app = FastAPI(title="ThresholdGuard API")

# Allow a local frontend dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/investigate")
def investigate():
    """
    Runs the full pipeline: Blue Agent investigates logs, each finding's
    proposed action is evaluated by the Governor (LLM advisory + OPA
    binding decision), stored, then the Pattern Auditor checks for
    cumulative risk across recent history.
    """
    try:
        findings = run_blue_agent_investigation()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blue Agent investigation failed: {e}")

    processed_actions = []
    for threat in findings.get("threats_detected", []):
        record = evaluate_action(threat["proposed_action"], threat["reasoning"])
        store_action(record)
        processed_actions.append(record)

    pattern_report = audit_recent_actions()

    return {
        "threats_detected": findings.get("threats_detected", []),
        "governed_actions": processed_actions,
        "pattern_audit": pattern_report,
    }


@app.get("/audit-trail")
def audit_trail(minutes: int = 60):
    """Returns the recent action history for display in a dashboard."""
    return {"actions": get_recent_actions(minutes=minutes)}


@app.get("/pattern-audit")
def pattern_audit():
    """Returns the current cumulative-risk pattern report on demand."""
    return audit_recent_actions()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)