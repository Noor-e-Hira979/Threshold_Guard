"""
llm_advisor.py
Governor's LLM reasoning layer. Produces an ADVISORY verdict + explanation
for a proposed action -- this is NEVER the final decision (OPA is), but it
gives human reviewers useful reasoning in the audit trail.

Includes a self-correction loop: if the LLM returns malformed output, it is
re-prompted with the validation error before giving up.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

ADVISOR_SYSTEM_PROMPT = """You are a security governance advisor. You will be given a proposed
remediation action (from a defensive security agent) along with the
reasoning that led to it. Your job is to assess how risky this action is
to execute autonomously, and explain your reasoning clearly.

You do NOT make the final decision -- a separate deterministic policy
engine does that. Your output is advisory only, used to help a human
reviewer understand the risk.

Respond ONLY with valid JSON in this exact structure, nothing else:
{
  "risk_assessment": "<low | medium | high>",
  "advisory_verdict": "<auto_approve | escalate | block>",
  "explanation": "<clear, plain-language reasoning for your assessment>"
}
"""

MAX_RETRIES = 2


def get_advisory_verdict(proposed_action: dict, detection_reasoning: str) -> dict:
    """
    Calls the LLM to produce an advisory risk assessment for a proposed
    action. Self-corrects up to MAX_RETRIES times if the model returns
    invalid JSON or missing required fields.
    """
    user_content = (
        f"Detection reasoning: {detection_reasoning}\n\n"
        f"Proposed action: {json.dumps(proposed_action)}"
    )

    messages = [
        {"role": "system", "content": ADVISOR_SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    attempt = 0
    while attempt <= MAX_RETRIES:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2,
        )
        raw_output = response.choices[0].message.content.strip()

        try:
            parsed = json.loads(raw_output)
            required_fields = {"risk_assessment", "advisory_verdict", "explanation"}
            if not required_fields.issubset(parsed.keys()):
                raise ValueError(f"Missing required fields. Got: {list(parsed.keys())}")
            if parsed["advisory_verdict"] not in ("auto_approve", "escalate", "block"):
                raise ValueError(f"Invalid advisory_verdict value: {parsed['advisory_verdict']}")
            return parsed

        except (json.JSONDecodeError, ValueError) as e:
            attempt += 1
            print(f"[!] Advisor output invalid (attempt {attempt}/{MAX_RETRIES}): {e}")
            if attempt > MAX_RETRIES:
                print("[!] Max retries exceeded. Failing safe.")
                return {
                    "risk_assessment": "high",
                    "advisory_verdict": "escalate",
                    "explanation": "LLM advisor failed to produce valid output after retries; failing safe.",
                }
            # Self-correction: feed the error back to the model and ask it to fix its output
            messages.append({"role": "assistant", "content": raw_output})
            messages.append({
                "role": "user",
                "content": f"Your previous output was invalid: {e}. "
                           f"Return ONLY the corrected valid JSON object, nothing else."
            })


if __name__ == "__main__":
    test_action = {
        "action_type": "patch_config",
        "target": "dvwa application",
        "scope": "all user accounts and database queries",
        "reversible": False,
    }
    test_reasoning = "SQL injection detected attempting to extract user credentials via UNION-based query."

    result = get_advisory_verdict(test_action, test_reasoning)
    print(json.dumps(result, indent=2))