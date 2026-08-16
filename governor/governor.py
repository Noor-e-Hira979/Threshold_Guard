"""
governor.py
The Governor: combines the LLM's advisory risk assessment with OPA's
binding, deterministic decision into a single audit record.

Core safety design: OPA's decision is ALWAYS final. The LLM's verdict is
recorded for transparency/human review, but never overrides OPA -- this is
what keeps the system safe even if the LLM is jailbroken or manipulated.
"""

import json
from datetime import datetime, timezone

from llm_advisor import get_advisory_verdict
from opa_client import get_opa_decision


def evaluate_action(proposed_action: dict, detection_reasoning: str) -> dict:
    """
    Runs a proposed action through both the LLM advisor and OPA, and
    returns a single combined audit record. OPA's decision is the
    authoritative outcome; the LLM's verdict is advisory context only.
    """
    advisory = get_advisory_verdict(proposed_action, detection_reasoning)
    final_decision = get_opa_decision(proposed_action)

    llm_opa_agreement = advisory["advisory_verdict"] == final_decision

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "proposed_action": proposed_action,
        "detection_reasoning": detection_reasoning,
        "llm_advisory": advisory,
        "final_decision": final_decision,  # <-- authoritative, from OPA
        "llm_opa_agreement": llm_opa_agreement,
    }

    print(f"[Governor] Final decision (OPA, authoritative): {final_decision.upper()}")
    print(f"[Governor] LLM advisory verdict was: {advisory['advisory_verdict']} "
          f"({'agrees' if llm_opa_agreement else 'DISAGREES -- OPA overrides'})")

    return record


if __name__ == "__main__":
    test_action = {
        "action_type": "patch_config",
        "target": "dvwa application",
        "scope": "all user accounts and database queries",
        "reversible": False,
    }
    test_reasoning = "SQL injection detected attempting to extract user credentials via UNION-based query."

    audit_record = evaluate_action(test_action, test_reasoning)
    print("\nFull audit record:")
    print(json.dumps(audit_record, indent=2))