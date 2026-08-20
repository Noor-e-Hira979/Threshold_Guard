## Running a live investigation (dashboard)
1. Make sure Docker, Ollama, and the backend are all running (see [[Installation]])
2. Generate fresh attack traffic:

cd red-agent
python sql_injection_attack.py

3. Open the frontend dashboard and click **Run Investigation**
4. Watch the mascot reflect pipeline state (analyzing -> approved/escalated/blocked)
5. Click **show evidence chain** on any result to see the Advisor's reasoning, the Supervisor's cross-check, and OPA's binding decision side by side

## Running via the API directly
POST http://localhost:8000/investigate
Headers: x-api-key: <your key>

Returns detected threats, governed actions (full evidence chain per action), and the current pattern-audit report.

Other endpoints:
- `GET /health` — no auth required
- `GET /audit-trail?minutes=60` — recent action history
- `GET /pattern-audit` — current cumulative-risk report on demand

## Running individual modules standalone (for testing/debugging)
Each module can be run directly:
python red-agent/sql_injection_attack.py
python red-agent/adversarial_planner.py
python blue-agent/blue_agent.py
python governor/governor.py
python pattern-auditor/pattern_auditor.py


## Running the evaluation suite
python evaluation/jailbreak_test.py
python evaluation/opa_robustness_test.py
python evaluation/log_injection_test.py
python evaluation/tamper_detection_test.py
Each writes a `_results.json` file with full details alongside console output.

## A note on response time
Local CPU inference means a full investigation can take 1-5+ minutes, especially when the Supervisor tier is involved. This is expected — see [[Tools & Tech Stack]] for why.