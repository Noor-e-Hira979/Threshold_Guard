# ThresholdGuard

An agentic AI security-governance system that decides how much autonomy to give AI agents during automated incident response. Instead of letting an autonomous agent execute security actions directly, ThresholdGuard places two layers of scrutiny between proposal and execution: an LLM-based Governor for reasoning and transparency, and a deterministic policy engine (OPA) that makes the final, binding decision — one that cannot be talked out of its rules, even if the LLM advisor is jailbroken. A separate Pattern Auditor watches the cumulative history of approved actions to catch a harder problem: an attacker (or a misaligned agent) splitting one harmful objective into many small, individually-approved actions to evade single-action governance entirely.

## The Problem

Autonomous security agents are increasingly expected to detect and remediate threats without waiting for a human — but nobody has solved how much autonomy is actually safe to hand them. Give an agent too much authority and one wrong action can cascade into an outage or a breach; give it too little and you're back to the alert-fatigue, slow-response problem autonomous agents were supposed to fix. This project treats that as the actual research question, rather than building another detection engine.

## Architecture

```
Red Agent / Adversarial Planning Agent
        │  (attacks a sandboxed target; the adversarial
        │   agent autonomously reasons about how to split
        │   a harmful objective into evasive sub-actions)
        ▼
Blue Agent (agentic, CrewAI + tool-calling)
        │  investigates logs, proposes a remediation action
        ▼
Governor
    ├── LLM Advisor  → advisory risk assessment (explanation only)
    └── OPA Policy   → BINDING decision: auto_approve / escalate / block
        ▼
Pattern Auditor
        │  scans rolling history of auto-approved actions for
        │  cumulative-risk patterns (normalized by category, not
        │  raw wording) that no single-action check could see
        ▼
Backend API (FastAPI) → audit trail, investigation trigger, pattern reports
```

**Core safety design:** the LLM Governor's verdict is never authoritative. OPA's decision is final and cannot be overridden by prompt manipulation, because it isn't reasoning over language at all — it's evaluating hard, pre-defined rules (Rego policies).

## Evaluation

We ran an adversarial jailbreak evaluation against the Governor: four proposed actions, each genuinely dangerous (broad scope, irreversible), paired with detection-reasoning text containing prompt-injection-style manipulation attempts (fake authority claims, urgency pressure, direct instruction overrides, false "this is safe" framing).

| Metric | Result |
|---|---|
| LLM advisor fooled rate | 1/4 (25%) |
| OPA correctly blocked/escalated regardless | 4/4 (100%) |

This is the project's central finding: **the LLM advisor can be manipulated, but system safety does not depend on it being unbreakable**, because the deterministic policy layer catches dangerous actions regardless of what the LLM was tricked into recommending.

We also validated the Pattern Auditor against a non-scripted adversarial agent (not a hardcoded test) that was given only a harmful objective and autonomously decided to split it into 5 individually-narrow, individually-auto-approved actions. Each action passed OPA's single-action check on its own merits — the Pattern Auditor correctly flagged the cumulative pattern across the sequence, using normalized action categories so the detection isn't defeated by differently-worded actions across runs.

## Tech Stack

| Layer | Technology |
|---|---|
| Sandboxed target | DVWA (Docker) |
| Red / Adversarial agent | Custom Python + Groq-hosted LLM reasoning |
| Blue agent | CrewAI (agentic, tool-calling), Groq |
| Governor — LLM advisor | Groq (`llama-3.1-8b-instant`) |
| Governor — policy engine | Open Policy Agent (Rego), Dockerized |
| Pattern Auditor | SQLite + LLM-based action classifier (normalizes wording into fixed categories) |
| Backend | FastAPI |
| Evaluation | Custom jailbreak test harness |

## Project Status: v1

This is the first working version. Complete and evaluated:
- [x] Sandboxed Docker target
- [x] Red Agent + autonomous Adversarial Planning Agent
- [x] Agentic Blue Agent (CrewAI, tool-calling, investigates before concluding)
- [x] Governor (LLM advisory layer)
- [x] OPA deterministic policy enforcement
- [x] Pattern Auditor (cumulative-risk detection, category-normalized)
- [x] Backend API tying the full pipeline together
- [x] Jailbreak evaluation with quantified results

Planned for future versions:
- [ ] Frontend dashboard (live action queue, audit trail viewer, attack simulation trigger)
- [ ] Observability tracing (Arize Phoenix) for full agent-hop visibility
- [ ] Migration from SQLite to PostgreSQL
- [ ] Expanded jailbreak test suite

## Setup

1. Start the sandbox + policy engine:
   ```
   docker-compose up -d
   ```
2. Initialize DVWA: open `http://localhost:8080`, log in (`admin`/`password`), click **Create/Reset Database**, set **DVWA Security** to **Low**.
3. Each module has its own `requirements.txt` — install per-folder:
   ```
   pip install -r <module>/requirements.txt --break-system-packages
   ```
4. Add a `.env` file (not committed) with `GROQ_API_KEY=your_key` in each module folder that needs it (`blue-agent/`, `governor/`, `pattern-auditor/`, `red-agent/`, `evaluation/`).
5. Run the backend:
   ```
   cd backend
   uvicorn main:app --reload --port 8000
   ```
   Visit `http://localhost:8000/docs` for the interactive API.
6. Run the jailbreak evaluation:
   ```
   cd evaluation
   python jailbreak_test.py
   ```

## Repo Structure

```
thresholdguard/
├── docker-compose.yml
├── red-agent/           # Red Agent + Adversarial Planning Agent
├── blue-agent/           # Agentic detection (CrewAI)
├── governor/              # LLM advisor + OPA client + policies
│   └── opa-policies/
├── pattern-auditor/        # Cumulative-risk detection + action classifier
├── backend/                # FastAPI orchestration layer
├── evaluation/              # Jailbreak red-teaming harness
└── frontend/                # (planned)
```