package thresholdguard

import rego.v1

never_auto_approve_types := {"revoke_account", "patch_config", "network_wide_lockdown"}

is_irreversible if {
    input.proposed_action.reversible == false
}

is_broad_scope if {
    contains(lower(input.proposed_action.scope), "all")
}

is_high_risk_type if {
    input.proposed_action.action_type in never_auto_approve_types
}

# Priority order: block > escalate > auto_approve > default escalate
decision := "block" if {
    is_high_risk_type
    is_irreversible
    is_broad_scope
} else := "escalate" if {
    is_irreversible
} else := "escalate" if {
    is_broad_scope
} else := "auto_approve" if {
    input.proposed_action.reversible == true
    not is_broad_scope
    not is_high_risk_type
} else := "escalate"