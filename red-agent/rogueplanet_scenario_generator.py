"""
rogueplanet_scenario_generator.py
Generates a REALISTIC, non-hardcoded simulated Windows event log excerpt
representing the RoguePlanet (CVE-2026-50656) privilege escalation pattern
-- an Improper Link Resolution (CWE-59) exploit against the Microsoft
Malware Protection Engine (mpengine.dll). Runs locally via Ollama.
"""

import json
import re
import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
GENERATOR_MODEL = "qwen2.5-coder:7b-instruct-q4_0"

GENERATOR_SYSTEM_PROMPT = """Generate a simulated Windows event log excerpt for CVE-2026-50656
("RoguePlanet") in Microsoft Defender's mpengine.dll (CWE-59: Improper
Link Resolution).
 
EXACT attack pattern to depict:
1. A low-privileged process creates a filesystem JUNCTION or REPARSE
   POINT (not a normal file) pointing at a path it shouldn't access.
2. This triggers a Defender scan on that path.
3. mpengine.dll, running as SYSTEM, FOLLOWS THE JUNCTION and performs a
   file operation on the attacker-controlled redirected target instead
   of the intended path -- this is the privilege escalation.
 
Generate 5-6 log lines as PLAIN TEXT STRINGS (not objects) showing:
junction/reparse point creation -> Defender scan triggered ->
mpengine.dll (SYSTEM) accessing the REDIRECTED path. Vary process
names/PIDs/timestamps. Use DOUBLE backslashes in file paths.
 
Respond ONLY with this JSON structure, nothing else:
{"scenario_name": "RoguePlanet (CVE-2026-50656) simulated exploitation attempt", "log_lines": ["<plain text log line 1>", "<plain text log line 2>"]}
"""

MAX_RETRIES = 2


def _sanitize_backslashes(raw: str) -> str:
    """Fixes the common LLM mistake of emitting single backslashes (e.g. in
    Windows file paths) inside JSON strings, where they must be escaped as
    double backslashes. Only touches backslashes NOT already part of a
    valid JSON escape sequence."""
    valid_escapes = set('"\\/bfnrtu')

    def fix(match):
        next_char = match.group(1)
        if next_char in valid_escapes:
            return "\\" + next_char
        return "\\\\" + next_char

    return re.sub(r'\\(.)', fix, raw)


def generate_rogueplanet_scenario() -> dict:
    """Generates a fresh, non-hardcoded simulated log excerpt for the
    RoguePlanet privilege escalation pattern. Output varies each run.
    Self-corrects if the model returns invalid JSON."""
    messages = [
        {"role": "system", "content": GENERATOR_SYSTEM_PROMPT},
        {"role": "user", "content": "Generate the simulated log excerpt now."},
    ]

    attempt = 0
    while attempt <= MAX_RETRIES:
        payload = {
            "model": GENERATOR_MODEL,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.8},
        }

        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
            resp.raise_for_status()
            raw_output = resp.json()["message"]["content"].strip()
        except requests.exceptions.RequestException as e:
            print(f"[!] Generator request failed: {e}")
            return {"scenario_name": "RoguePlanet (request failed)", "log_lines": []}

        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass

        sanitized = _sanitize_backslashes(raw_output)
        try:
            return json.loads(sanitized)
        except json.JSONDecodeError as e:
            attempt += 1
            if attempt > MAX_RETRIES:
                print(f"[!] Generator returned invalid JSON after {MAX_RETRIES} retries: {e}")
                print(raw_output)
                return {"scenario_name": "RoguePlanet (generation failed)", "log_lines": []}
            messages.append({"role": "assistant", "content": raw_output})
            messages.append({
                "role": "user",
                "content": (
                    "Your JSON was invalid -- likely due to unescaped backslashes in "
                    "Windows file paths. Return ONLY corrected valid JSON, using DOUBLE "
                    "backslashes for every backslash in file paths."
                )
            })


if __name__ == "__main__":
    scenario = generate_rogueplanet_scenario()
    print(f"Scenario: {scenario['scenario_name']}\n")
    for line in scenario["log_lines"]:
        print(line)