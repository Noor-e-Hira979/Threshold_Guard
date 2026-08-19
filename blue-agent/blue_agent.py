"""
blue_agent.py
Agentic Blue Agent -- CUSTOM implementation using Ollama's native tool-calling
API directly, bypassing CrewAI/litellm entirely. This permanently avoids a
known litellm<->Ollama multi-turn tool-calling compatibility bug.

The agent still has genuine autonomy: it decides for itself which tool(s)
to call, how many times, and when it has enough information to conclude --
this is a hand-rolled ReAct-style loop, not a scripted sequence.
"""

import os
import sys
import json
import requests

from log_fetcher import fetch_access_logs

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "red-agent"))
from rogueplanet_scenario_generator import generate_rogueplanet_scenario

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5-coder:7b-instruct-q4_0"
MAX_ITER = 3

SYSTEM_PROMPT = """You are an experienced SOC (Security Operations Center) analyst.
Investigate for malicious activity using the tools available to you. You
have two tools: fetch_recent_access_logs (web application logs -- SQLi,
brute force, recon) and fetch_endpoint_security_logs (OS-level endpoint
logs -- privilege escalation via junction/reparse point manipulation,
e.g. CVE-2026-50656 "RoguePlanet"-style attacks). Use whichever tool(s)
are relevant.

CRITICAL: Your final answer must be your ANALYSIS, never the raw log
lines themselves. If you see SQL syntax like 'UNION SELECT', that is SQL
injection. If you see a process creating a junction/reparse point followed
by a privileged process (e.g. mpengine.dll, running as SYSTEM) accessing
a redirected/unexpected file path, that is a privilege escalation attempt.

Once you have investigated enough, respond with ONLY valid JSON in this
exact structure, with no other text:
{"threats_detected": [{"log_line": "the specific log line showing the attack",
"attack_type": "short label like sql_injection or privilege_escalation",
"reasoning": "why this is malicious, in plain language",
"proposed_action": {"action_type": "...", "target": "...", "scope": "...",
"reversible": true or false}}]}
If no threats are found, respond with exactly: {"threats_detected": []}
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_recent_access_logs",
            "description": (
                "Fetches the most recent lines of the DVWA web application's "
                "Apache access log. Use to investigate web application activity "
                "(SQLi, brute force, recon)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "num_lines": {"type": "integer", "description": "Number of log lines to fetch (default 15)"}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_endpoint_security_logs",
            "description": (
                "Fetches a simulated excerpt of OS-level endpoint security "
                "event logs (Windows Security/Sysmon style). Use to investigate "
                "endpoint/privilege-escalation activity, distinct from web logs."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def _execute_tool(name: str, args: dict) -> str:
    """Executes the real Python function behind a tool call."""
    if name == "fetch_recent_access_logs":
        num_lines = args.get("num_lines", 15)
        lines = fetch_access_logs(lines=num_lines)
        return "\n".join(lines) if lines else "No log lines were retrieved."
    elif name == "fetch_endpoint_security_logs":
        scenario = generate_rogueplanet_scenario()
        lines = scenario.get("log_lines", [])
        return "\n".join(lines) if lines else "No endpoint log lines were retrieved."
    else:
        return f"Unknown tool: {name}"


def analyze_log_text(log_text: str) -> dict:
    """
    Runs the Blue Agent's reasoning directly on PRE-SUPPLIED log text,
    bypassing the tool-fetch step. Used for controlled evaluation (e.g.
    log injection testing) where we need to feed specific, crafted log
    content rather than live data.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this log data for malicious activity:\n\n{log_text}"},
    ]

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.2},
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=180)
        resp.raise_for_status()
        raw_output = resp.json()["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        print(f"[!] Analysis request failed: {e}")
        return {"threats_detected": []}

    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        if raw_output.startswith("json"):
            raw_output = raw_output[4:].strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        print("[!] Analysis did not return valid JSON. Raw output:")
        print(raw_output)
        return {"threats_detected": []}


def run_blue_agent_investigation() -> dict:
    """
    Runs the custom agentic loop: the model decides which tool(s) to call
    and when it has enough evidence to conclude, up to MAX_ITER rounds.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Investigate for malicious activity now."},
    ]

    for iteration in range(MAX_ITER):
        payload = {
            "model": MODEL,
            "messages": messages,
            "tools": TOOLS,
            "stream": False,
            "options": {"temperature": 0.2},
        }

        try:
            resp = requests.post(OLLAMA_URL, json=payload, timeout=300)
            resp.raise_for_status()
            message = resp.json()["message"]
        except requests.exceptions.RequestException as e:
            print(f"[!] Blue Agent request failed: {e}")
            return {"threats_detected": []}

        tool_calls = message.get("tool_calls")

        if tool_calls:
            messages.append(message)
            for call in tool_calls:
                fn_name = call["function"]["name"]
                fn_args = call["function"].get("arguments", {})
                if isinstance(fn_args, str):
                    fn_args = json.loads(fn_args) if fn_args else {}
                print(f"[Blue Agent] Calling tool: {fn_name}({fn_args})")
                result = _execute_tool(fn_name, fn_args)
                messages.append({"role": "tool", "content": result})
            continue  # let the model reason over the tool result

        # No structured tool call -- treat this as the final answer
        raw_output = message.get("content", "").strip()
        if raw_output.startswith("```"):
            raw_output = raw_output.strip("`")
            if raw_output.startswith("json"):
                raw_output = raw_output[4:].strip()

        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError:
            print("[!] Blue Agent did not return valid JSON. Raw output:")
            print(raw_output)
            return {"threats_detected": []}

        # Fallback: some smaller models emit a tool call as plain-text JSON
        # in "content" instead of populating the structured tool_calls field.
        # Detect that shape and handle it as a real tool call instead of a
        # final answer.
        if "name" in parsed and "arguments" in parsed and "threats_detected" not in parsed:
            fn_name = parsed["name"]
            fn_args = parsed["arguments"]
            print(f"[Blue Agent] (fallback) Detected tool call in content: {fn_name}({fn_args})")
            result = _execute_tool(fn_name, fn_args)
            messages.append({"role": "assistant", "content": raw_output})
            messages.append({"role": "tool", "content": result})
            continue

        return parsed

    print("[!] Blue Agent reached max iterations without a final answer.")
    return {"threats_detected": []}


if __name__ == "__main__":
    findings = run_blue_agent_investigation()
    print("\n=== Raw findings (debug) ===")
    print(json.dumps(findings, indent=2))

    print("\n=== Blue Agent Findings ===")
    threats = findings.get("threats_detected", [])
    if not threats:
        print("[-] No threats detected.")
    else:
        for threat in threats:
            print(f"[!] {threat['attack_type']}: {threat['reasoning']}")
            print(f"    Proposed action: {threat['proposed_action']}\n")