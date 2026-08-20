
## Module breakdown

| Module | Folder | Responsibility |
|---|---|---|
| Sandboxed target | `docker-compose.yml` | DVWA (vulnerable web app) + OPA, isolated containers |
| Red Agent | `red-agent/` | Executes real SQL injection against DVWA |
| Adversarial Planning Agent | `red-agent/adversarial_planner.py` | Autonomously plans how to split a harmful objective into evasive sub-actions |
| RoguePlanet Generator | `red-agent/rogueplanet_scenario_generator.py` | Generates realistic simulated logs for CVE-2026-50656, a second attack scenario type |
| Blue Agent | `blue-agent/` | Custom tool-calling agent (no framework dependency), investigates logs, proposes actions |
| Detection Auditor | `blue-agent/detection_auditor.py` | Deterministic signature-scan backstop for the Blue Agent |
| Governor | `governor/` | Advisor + Supervisor + OPA client, combines into one audit record |
| OPA Policies | `governor/opa-policies/` | Rego rules — the actual binding decision logic |
| Pattern Auditor | `pattern-auditor/` | SQLite-backed action history, category-normalized cumulative-risk detection, hash-chained audit trail |
| Backend | `backend/` | FastAPI orchestration, API-key protected endpoints |
| Evaluation | `evaluation/` | Jailbreak, OPA robustness, log injection, and tamper-detection test harnesses |
| Frontend | `frontend/` | React + Tailwind dashboard and public-facing site |

## Core safety design
Neither LLM tier's verdict is ever authoritative. OPA's decision is final and cannot be overridden by prompt manipulation, because it isn't reasoning over language — it's evaluating hard, pre-defined rules. See [[Security Considerations]] for why this matters and what it doesn't cover.