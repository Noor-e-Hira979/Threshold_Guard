"""
opa_client.py
Sends a proposed action to OPA and returns its deterministic decision.
This is the final, authoritative decision -- it overrides whatever the
LLM Governor advises, per ThresholdGuard's core safety design.
"""

import requests

OPA_URL = "http://localhost:8181/v1/data/thresholdguard/decision"


def get_opa_decision(proposed_action: dict) -> str:
    """
    Queries OPA with a proposed action and returns one of:
    "auto_approve", "escalate", or "block".
    Fails safe: if OPA is unreachable or errors, defaults to "escalate"
    rather than silently allowing an action through.
    """
    payload = {"input": {"proposed_action": proposed_action}}

    try:
        resp = requests.post(OPA_URL, json=payload, timeout=5)
        resp.raise_for_status()
        result = resp.json().get("result")
        if result not in ("auto_approve", "escalate", "block"):
            print(f"[!] OPA returned unexpected result: {result}. Failing safe to 'escalate'.")
            return "escalate"
        return result
    except requests.exceptions.RequestException as e:
        print(f"[!] Could not reach OPA ({e}). Failing safe to 'escalate'.")
        return "escalate"


if __name__ == "__main__":
    test_action = {
        "action_type": "patch_config",
        "target": "dvwa application",
        "scope": "all user accounts and database queries",
        "reversible": False,
    }
    print(get_opa_decision(test_action))