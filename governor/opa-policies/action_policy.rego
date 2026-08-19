package thresholdguard

import rego.v1

# ALLOWLIST -- only these action types may ever be auto-approved.
# Anything not explicitly listed here is NOT safe by default (fail-safe).
known_safe_auto_approve_types := {"block_ip", "revoke_single_session", "input_validation"}

# Hard blocklist -- these action types are never even eligible for
# auto-approval, and combined with irreversible + broad scope, are blocked
# outright rather than merely escalated.
never_block_types := {"revoke_account", "patch_config", "network_wide_lockdown"}

is_irreversible if {
    input.proposed_action.reversible == false
}

is_broad_scope if {
    regex.match(`(?i)\ball\b`, input.proposed_action.scope)
}

is_hard_block_type if {
    input.proposed_action.action_type in never_block_types
}

is_known_safe_type if {
    input.proposed_action.action_type in known_safe_auto_approve_types
}

# Single decision chain, evaluated in priority order:
# block > escalate (irreversible) > escalate (broad scope) >
# auto_approve (only if explicitly allowlisted, reversible, narrow) >
# default escalate (fail-safe for anything not explicitly allowlisted)
decision := "block" if {
    is_hard_block_type
    is_irreversible
    is_broad_scope
} else := "escalate" if {
    is_irreversible
} else := "escalate" if {
    is_broad_scope
} else := "auto_approve" if {
    input.proposed_action.reversible == true
    not is_broad_scope
    is_known_safe_type
} else := "escalate"