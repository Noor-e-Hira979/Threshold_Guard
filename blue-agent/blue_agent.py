"""
blue_agent.py
Agentic version of the Blue Agent using CrewAI. Has fetch_recent_access_logs
as a real tool it can decide to call (including multiple times if needed),
giving it genuine multi-step investigative autonomy rather than a single
fixed prompt-and-parse call.
"""

import os
import json
import time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

from log_fetcher import fetch_access_logs

load_dotenv()

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.2,
    max_retries=3,
)


@tool("fetch_recent_access_logs")
def fetch_recent_access_logs_tool(num_lines: int = 15) -> str:
    """Fetches the most recent N lines of the target application's Apache
    access log (default 15, keep small to conserve tokens). Use this to
    investigate suspicious activity. You may call this again with a
    slightly larger num_lines only if truly necessary."""
    lines = fetch_access_logs(lines=num_lines)
    if not lines:
        return "No log lines were retrieved. The target container may be unreachable."
    return "\n".join(lines)


blue_agent = Agent(
    role="Defensive Security Analyst",
    goal=(
        "Investigate access logs from the target application to identify malicious "
        "behavior (SQL injection, brute force, reconnaissance, or other attacks), "
        "explain the reasoning behind each finding, and propose one specific, "
        "narrowly-scoped remediation action per distinct threat found."
    ),
    backstory=(
        "You are an experienced SOC analyst. You investigate logs thoroughly, "
        "then ALWAYS report your conclusions as structured findings -- you never "
        "output raw log lines as your final answer, since that would be useless "
        "to a human reviewer who needs your analysis, not the raw data they could "
        "have read themselves."
    ),
    tools=[fetch_recent_access_logs_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False,
    max_iter=2,
)


def run_blue_agent_investigation(max_retries: int = 3) -> dict:
    """Runs the agentic Blue Agent investigation and returns structured findings.
    Retries with backoff if a rate limit (429) error is hit."""
    task = Task(
        description=(
            "Investigate the target application's recent access logs for malicious "
            "activity using the fetch_recent_access_logs tool.\n\n"
            "CRITICAL: Your final answer must be your ANALYSIS, never the raw log "
            "lines themselves. If you see a request containing SQL syntax like "
            "'UNION SELECT', that is a SQL injection attempt -- report it as a "
            "finding, do not just repeat the log line.\n\n"
            "Your final answer must be ONLY valid JSON in this exact structure, "
            "with no other text before or after it:\n"
            '{"threats_detected": [{"log_line": "the specific log line that shows '
            'the attack", "attack_type": "short label like sql_injection", '
            '"reasoning": "why this is malicious, in plain language", '
            '"proposed_action": {"action_type": "...", "target": "...", '
            '"scope": "...", "reversible": true or false}}]}\n\n'
            'If no threats are found after investigating, return exactly: '
            '{"threats_detected": []}'
        ),
        expected_output=(
            "ONLY a JSON object matching the exact structure described above. "
            "Never raw log lines. Never explanatory text outside the JSON."
        ),
        agent=blue_agent,
    )

    crew = Crew(agents=[blue_agent], tasks=[task], verbose=True)

    result = None
    for attempt in range(1, max_retries + 1):
        try:
            result = crew.kickoff()
            break
        except Exception as e:
            if "429" in str(e) and attempt < max_retries:
                wait_time = 20 * attempt
                print(f"[!] Rate limit hit (attempt {attempt}/{max_retries}). "
                      f"Waiting {wait_time}s before retrying...")
                time.sleep(wait_time)
            else:
                raise

    raw_output = str(result).strip()
    if raw_output.startswith("```"):
        raw_output = raw_output.strip("`")
        if raw_output.startswith("json"):
            raw_output = raw_output[4:].strip()

    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        print("[!] Blue Agent did not return valid JSON. Raw output:")
        print(raw_output)
        return {"threats_detected": []}


if __name__ == "__main__":
    findings = run_blue_agent_investigation()
    print("\n=== Blue Agent Findings ===")
    if not findings["threats_detected"]:
        print("[-] No threats detected.")
    else:
        for threat in findings["threats_detected"]:
            print(f"[!] {threat['attack_type']}: {threat['reasoning']}")
            print(f"    Proposed action: {threat['proposed_action']}\n")