"""
main.py
FastAPI backend tying together the full ThresholdGuard pipeline:
Blue Agent (detection) -> Governor (LLM advisory + OPA binding decision)
-> Pattern Auditor (cumulative risk check).

Exposes REST endpoints so a frontend dashboard (or any client) can trigger
an investigation and view the audit trail. The /investigate endpoint
requires a shared-secret API key so arbitrary network callers cannot feed
fabricated proposed actions directly into the Governor.
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "blue-agent"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "governor"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "pattern-auditor"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "red-agent"))

from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from blue_agent import run_blue_agent_investigation
from governor import evaluate_action
from action_store import init_db, store_action, get_recent_actions
from pattern_auditor import audit_recent_actions

load_dotenv()

API_KEY = os.environ.get("THRESHOLDGUARD_API_KEY", "dev-only-change-me")

app = FastAPI(title="ThresholdGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def verify_api_key(x_api_key: str = Header(None)):
    """Simple shared-secret auth. Blocks unauthenticated submissions to
    the pipeline -- closes the gap where anyone with network access could
    feed fabricated proposed actions straight into the Governor."""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/investigate")
def investigate(authorized: bool = Depends(verify_api_key)):
    """
    Runs the full pipeline: Blue Agent investigates logs, each finding's
    proposed action is evaluated by the Governor (LLM advisory + OPA
    binding decision), stored, then the Pattern Auditor checks for
    cumulative risk across recent history. Requires a valid X-API-Key header.
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
    "blue_agent_status": findings.get("status", "unknown"),
    "blue_agent_error": findings.get("error_detail"),
    "threats_detected": findings.get("threats_detected", []),
    "governed_actions": processed_actions,
    "pattern_audit": pattern_report,
}

@app.get("/audit-trail")
def audit_trail(minutes: int = 60, authorized: bool = Depends(verify_api_key)):
    """Returns the recent action history for display in a dashboard."""
    return {"actions": get_recent_actions(minutes=minutes)}


@app.get("/pattern-audit")
def pattern_audit(authorized: bool = Depends(verify_api_key)):
    """Returns the current cumulative-risk pattern report on demand."""
    return audit_recent_actions()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)