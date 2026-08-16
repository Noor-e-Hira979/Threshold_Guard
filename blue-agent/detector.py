"""
detector.py
Blue Agent: analyzes raw access logs using LLM-based reasoning to identify
malicious behavior (e.g. SQL injection patterns), then proposes a
remediation action. This proposed action is NOT executed here -- it gets
passed to the Governor + OPA policy layer for evaluation.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq
from log_fetcher import fetch_access_logs

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DETECTION_SYSTEM_PROMPT = """You are a security analyst reviewing raw Apache access logs from a web
application. Your job is to identify requests that show malicious behavior
(such as SQL injection, brute force login attempts, or reconnaissance/scanning),
explain WHY each one is malicious in plain language, and propose ONE
remediation action per distinct threat you find.

Respond ONLY with valid JSON in this exact structure, nothing else:
{
  "threats_detected": [
    {
      "log_line": "<the raw log line that triggered detection>",
      "attack_type": "<short label, e.g. sql_injection>",
      "reasoning": "<why this is malicious, in plain language>",
      "proposed_action": {
        "action_type": "<e.g. block_ip | revoke_account | patch_config>",
        "target": "<what the action would apply to, e.g. an IP or account>",
        "scope": "<what this action would affect -- be specific>",
        "reversible": true or false
      }
    }
  ]
}
If no threats are found, return {"threats_detected": []}.
"""


def detect_threats(log_lines: list[str]) -> dict:
    """Sends log lines to the LLM for reasoning-based threat detection."""
    if not log_lines:
        return {"threats_detected": []}

    logs_text = "\n".join(log_lines)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": DETECTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Analyze these access logs:\n\n{logs_text}"},
        ],
        temperature=0.2,
    )

    raw_output = response.choices[0].message.content.strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        print("[!] LLM did not return valid JSON. Raw output was:")
        print(raw_output)
        return {"threats_detected": []}


if __name__ == "__main__":
    logs = fetch_access_logs()
    print(f"[+] Fetched {len(logs)} log lines. Analyzing...\n")

    findings = detect_threats(logs)

    if not findings["threats_detected"]:
        print("[-] No threats detected.")
    else:
        for threat in findings["threats_detected"]:
            print(f"[!] Detected: {threat['attack_type']}")
            print(f"    Reasoning: {threat['reasoning']}")
            print(f"    Proposed action: {threat['proposed_action']}\n")