"""
governor.py
The Governor: runs a proposed action through the full two-tier LLM check
(fast Advisor -> stronger Supervisor cross-check) plus OPA's binding
decision, combining everything into a single audit record.

Core safety design: OPA's decision is ALWAYS final. Neither LLM tier can
override it -- this is what keeps the system safe even if one or both
LLMs are manipulated. Both LLM tiers now run locally via Ollama.
"""

import json
from datetime import datetime, timezone

from llm_advisor import get_advisory_verdict
from opa_client import get_opa_decision
from supervisor import supervise_advisory


def evaluate_action(proposed_action: dict, detection_reasoning: str) -> dict:
    """
    Runs a proposed action through the full two-tier Governor: the fast
    Advisor produces an initial risk assessment, the stronger Supervisor
    cross-checks that assessment for signs of manipulation, and OPA makes
    the final BINDING decision -- unaffected by either LLM tier, per
    ThresholdGuard's core safety design.
    """
    advisory = get_advisory_verdict(proposed_action, detection_reasoning)
    supervision = supervise_advisory(proposed_action, advisory)
    final_decision = get_opa_decision(proposed_action)

    llm_opa_agreement = advisory["advisory_verdict"] == final_decision

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "proposed_action": proposed_action,
        "detection_reasoning": detection_reasoning,
        "llm_advisory": advisory,
        "supervisor_check": supervision,
        "final_decision": final_decision,  # <-- authoritative, from OPA
        "llm_opa_agreement": llm_opa_agreement,
    }

    print(f"[Governor] Final decision (OPA, authoritative): {final_decision.upper()}")
    print(f"[Governor] LLM advisory verdict was: {advisory['advisory_verdict']} "
          f"({'agrees' if llm_opa_agreement else 'DISAGREES -- OPA overrides'})")
    print(f"[Governor] Supervisor cross-check: "
          f"{'MANIPULATION SUSPECTED' if supervision['manipulation_suspected'] else 'advisor reasoning holds up'}")

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