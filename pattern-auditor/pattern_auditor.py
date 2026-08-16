"""
pattern_auditor.py
Core research contribution of ThresholdGuard.

Individually, the Governor + OPA evaluate ONE proposed action at a time.
An attacker (or a compromised/manipulated agent) can exploit this by
splitting one harmful objective into many small actions that each pass
the single-action check individually. The Pattern Auditor detects this by
analyzing the ROLLING HISTORY of recently auto-approved actions
collectively, grouping by NORMALIZED CATEGORY (not raw wording) so
differently-phrased actions with the same underlying effect are still
recognized as one pattern.
"""

from collections import defaultdict
from action_store import get_recent_actions

REPEAT_TARGET_THRESHOLD = 3
SAME_TYPE_BURST_THRESHOLD = 5
WINDOW_MINUTES = 10


def audit_recent_actions() -> dict:
    """
    Scans recently auto-approved actions for cumulative-risk patterns.
    Returns a report describing any detected pattern, or a clean result
    if nothing suspicious was found.
    """
    recent = get_recent_actions(minutes=WINDOW_MINUTES)
    auto_approved = [r for r in recent if r["final_decision"] == "auto_approve"]

    findings = []

    # Pattern 1: same target hit repeatedly
    target_counts = defaultdict(list)
    for record in auto_approved:
        target_counts[record["proposed_action"]["target"]].append(record)

    for target, records in target_counts.items():
        if len(records) >= REPEAT_TARGET_THRESHOLD:
            findings.append({
                "pattern_type": "repeated_target",
                "target": target,
                "occurrence_count": len(records),
                "explanation": (
                    f"'{target}' was targeted by {len(records)} separate auto-approved "
                    f"actions within {WINDOW_MINUTES} minutes. Individually each passed "
                    f"as low-risk, but the cumulative effect on this single target should "
                    f"be reviewed as if it were one combined action."
                ),
                "recommendation": "freeze_further_auto_approvals_for_target",
                "affected_records": [r["timestamp"] for r in records],
            })

    # Pattern 2: burst of same-CATEGORY actions (normalized, not raw string --
    # catches "Account Isolation", "Account Lockout", "revoke_single_session"
    # as the SAME underlying pattern even though worded differently)
    category_counts = defaultdict(list)
    for record in auto_approved:
        category = record.get("normalized_category", "other")
        category_counts[category].append(record)

    for category, records in category_counts.items():
        if len(records) >= SAME_TYPE_BURST_THRESHOLD:
            findings.append({
                "pattern_type": "same_category_burst",
                "normalized_category": category,
                "occurrence_count": len(records),
                "explanation": (
                    f"{len(records)} actions classified as '{category}' were auto-approved "
                    f"within {WINDOW_MINUTES} minutes, even though they may have been worded "
                    f"differently. This volume, taken together, resembles a single large-scale "
                    f"action that OPA would normally escalate or block if proposed as one request."
                ),
                "recommendation": "freeze_further_auto_approvals_for_category",
                "affected_records": [r["timestamp"] for r in records],
            })

    return {
        "window_minutes": WINDOW_MINUTES,
        "total_auto_approved_in_window": len(auto_approved),
        "patterns_detected": findings,
        "cumulative_risk_flagged": len(findings) > 0,
    }


if __name__ == "__main__":
    report = audit_recent_actions()
    if report["cumulative_risk_flagged"]:
        print("[!] CUMULATIVE RISK DETECTED:")
        for finding in report["patterns_detected"]:
            print(f"  - {finding['pattern_type']}: {finding['explanation']}")
    else:
        print("[-] No cumulative risk patterns detected in recent history.")