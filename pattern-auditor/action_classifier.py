"""
action_classifier.py
Normalizes a proposed action's free-text action_type/target/scope into one
of a FIXED set of canonical categories, so the Pattern Auditor can group
semantically similar actions together even when different agents (or the
same agent on different runs) phrase them differently -- e.g. "Account
Isolation", "Account Lockout", and "revoke_single_session" should all be
recognized as the same underlying category of action.

Includes a self-correction retry loop, same pattern as llm_advisor.py.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Fixed taxonomy -- the Pattern Auditor groups by these categories, not raw strings.
CANONICAL_CATEGORIES = [
    "account_access_change",   # revoke, lockout, isolate, disable an account/session
    "network_block",           # block IP, firewall rule, isolate device from network
    "config_patch",            # modify application/system configuration
    "privilege_change",        # grant/revoke permissions or roles
    "data_access_restriction", # restrict/revoke data access, encryption key rotation
    "other",
]

CLASSIFIER_SYSTEM_PROMPT = f"""You classify a proposed security action into exactly ONE of these fixed
categories, based on its underlying effect, not its wording:

{json.dumps(CANONICAL_CATEGORIES)}

Respond ONLY with valid JSON in this exact structure, nothing else:
{{"category": "<one of the categories above, exactly as written>"}}
"""

MAX_RETRIES = 2


def classify_action(proposed_action: dict) -> str:
    """
    Maps a proposed action to a canonical category. Self-corrects if the
    LLM returns a category outside the fixed taxonomy. Falls back to
    "other" if classification fails after retries -- never crashes the
    pipeline over a classification failure.
    """
    user_content = f"Proposed action: {json.dumps(proposed_action)}"
    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    attempt = 0
    while attempt <= MAX_RETRIES:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.0,
        )
        raw_output = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw_output)
            category = parsed.get("category")
            if category not in CANONICAL_CATEGORIES:
                raise ValueError(f"'{category}' is not in the fixed taxonomy")
            return category
        except (json.JSONDecodeError, ValueError) as e:
            attempt += 1
            if attempt > MAX_RETRIES:
                print(f"[!] Classification failed after retries ({e}). Falling back to 'other'.")
                return "other"
            messages.append({"role": "assistant", "content": raw_output})
            messages.append({
                "role": "user",
                "content": f"Invalid: {e}. Return ONLY corrected JSON with a category from the fixed list."
            })


if __name__ == "__main__":
    test_actions = [
        {"action_type": "Account Isolation", "target": "user123", "scope": "single account"},
        {"action_type": "revoke_single_session", "target": "user456", "scope": "single account session"},
        {"action_type": "Account Lockout", "target": "user789", "scope": "one account"},
    ]
    for action in test_actions:
        category = classify_action(action)
        print(f"{action['action_type']:30s} -> {category}")