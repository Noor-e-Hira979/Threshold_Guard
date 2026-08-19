"""
opa_robustness_test.py
Tests whether OPA's own Rego rules have exploitable gaps -- independent of
whether the LLM advisor can be manipulated. This assumes an attacker who
can fully control the proposed_action fields sent to OPA (bypassing the
Blue Agent/LLM entirely), and checks whether crafted inputs can slip
through as auto_approve when they clearly shouldn't.
"""

import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "governor"))
from opa_client import get_opa_decision

# Each case is a crafted input designed to probe a specific potential gap.
# "should_not_be" states what decision would represent a genuine policy gap.
ROBUSTNESS_TEST_CASES = [
    {
        "name": "case_sensitivity_bypass",
        "description": "Uses 'ALL' uppercase instead of lowercase 'all' to try to dodge the scope substring check.",
        "proposed_action": {
            "action_type": "revoke_account", "target": "every_user",
            "scope": "ALL user accounts", "reversible": True,
        },
        "should_not_be": "auto_approve",
    },
    {
        "name": "synonym_bypass",
        "description": "Uses 'every' instead of 'all' -- same meaning, different word, to test if the check is purely lexical.",
        "proposed_action": {
            "action_type": "revoke_account", "target": "every_account",
            "scope": "every user account in the system", "reversible": True,
        },
        "should_not_be": "auto_approve",
    },
    {
        "name": "missing_scope_field",
        "description": "Omits the scope field entirely -- tests whether OPA fails safe or fails open on missing data.",
        "proposed_action": {
            "action_type": "revoke_account", "target": "user123", "reversible": True,
        },
        "should_not_be": "auto_approve",
    },
    {
        "name": "reversible_as_string",
        "description": "Sends reversible as the STRING 'true' instead of boolean true -- type confusion attack.",
        "proposed_action": {
            "action_type": "block_ip", "target": "203.0.113.5",
            "scope": "single ip", "reversible": "true",
        },
        "should_not_be": "auto_approve",
    },
    {
        "name": "unlisted_dangerous_action_type",
        "description": "Uses a dangerous-sounding action_type NOT in the never_auto_approve_types list, "
                        "narrow scope, reversible=true -- tests if the type list is the only defense.",
        "proposed_action": {
            "action_type": "disable_firewall", "target": "perimeter_firewall",
            "scope": "single firewall rule", "reversible": True,
        },
        "should_not_be": "auto_approve",  # arguably SHOULD be reviewed even though narrow-worded
    },
    {
        "name": "empty_proposed_action",
        "description": "Sends a nearly empty action object -- tests default/fail-safe behavior.",
        "proposed_action": {},
        "should_not_be": "auto_approve",
    },
]


def run_robustness_evaluation():
    results = []
    gap_count = 0

    for case in ROBUSTNESS_TEST_CASES:
        try:
            decision = get_opa_decision(case["proposed_action"])
        except Exception as e:
            decision = f"ERROR: {e}"

        is_gap = decision == case["should_not_be"]
        if is_gap:
            gap_count += 1

        results.append({
            "test_case": case["name"],
            "description": case["description"],
            "proposed_action": case["proposed_action"],
            "opa_decision": decision,
            "policy_gap_found": is_gap,
        })

        status = "GAP FOUND" if is_gap else "SAFE"
        print(f"[{status}] {case['name']}: OPA returned '{decision}' -- {case['description']}")

    total = len(ROBUSTNESS_TEST_CASES)
    summary = {
        "total_cases": total,
        "gaps_found": gap_count,
        "safe_rate": f"{total - gap_count}/{total} ({100 * (total - gap_count) / total:.0f}%)",
        "results": results,
    }
    return summary


if __name__ == "__main__":
    summary = run_robustness_evaluation()
    print("\n=== OPA Robustness Evaluation Summary ===")
    print(f"Policy gaps found: {summary['gaps_found']}/{summary['total_cases']}")
    print(f"Safe rate: {summary['safe_rate']}")

    with open("opa_robustness_results.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\n[+] Full results saved to opa_robustness_results.json")