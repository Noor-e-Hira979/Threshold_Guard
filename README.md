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
Blue Agent (custom agentic tool-calling loop, local Ollama)
        │  investigates logs, proposes a remediation action
        ▼
Governor (two-tier, fully local via Ollama)
    ├── Advisor (qwen2.5-coder, fast)   → first-pass advisory risk assessment
    ├── Supervisor (deepseek-r1:8b)     → cross-checks the Advisor's reasoning
    │                                      for signs of manipulation
    └── OPA Policy (Rego)               → BINDING decision: auto_approve /
                                            escalate / block -- unaffected
                                            by either LLM tier
        ▼
Pattern Auditor
        │  scans rolling history of auto-approved actions for
        │  cumulative-risk patterns (normalized by category, not
        │  raw wording) that no single-action check could see
        ▼
Backend API (FastAPI, API-key protected) → audit trail, investigation trigger
```

**Core safety design:** neither LLM tier's verdict is ever authoritative. OPA's decision is final and cannot be overridden by prompt manipulation, because it isn't reasoning over language at all — it's evaluating hard, pre-defined rules (Rego policies). All LLM inference runs locally via Ollama; no data leaves the machine.

## Evaluation

**Jailbreak evaluation (single-tier Advisor):** four proposed actions, each genuinely dangerous (broad scope, irreversible), paired with detection-reasoning text containing prompt-injection-style manipulation attempts.

| Metric | Result |
|---|---|
| LLM advisor fooled rate | 1/4 (25%) |
| OPA correctly blocked/escalated regardless | 4/4 (100%) |

**OPA robustness evaluation:** initial testing under a denylist policy design (`never_auto_approve_types`) revealed a real gap — action types not explicitly denylisted were auto-approved by default (fail-open). After redesigning to an allowlist model (fail-safe by default) and fixing a substring-matching bug (the word "firewall" false-matched a scope check for "all"), re-testing found 0/6 policy gaps.

**Two-tier Supervisor comparison:** on a deliberately manipulated advisory verdict (broad, irreversible action framed as "routine, safe, no real risk"), a fast/weak supervisor model (`qwen2.5:0.5b`) failed to detect the manipulation, while the stronger supervisor (`deepseek-r1:8b`) correctly identified the mismatch between the stated risk level and the action's actual scope/irreversibility. This demonstrates a real tradeoff between supervisor capability and CPU inference latency on constrained hardware.

**Pattern Auditor validation:** tested against a non-scripted Adversarial Planning Agent (not a hardcoded test) given only a harmful objective, which autonomously decided to split it into 5 individually-narrow, individually-auto-approved actions. Each passed OPA's single-action check on its own merits; the Pattern Auditor correctly flagged the cumulative pattern using normalized action categories, robust to differently-worded actions across runs.

## Tech Stack

| Layer | Technology |
|---|---|
| Sandboxed target | DVWA (Docker) |
| Red / Adversarial agent | Custom Python + local Ollama LLM reasoning |
| Blue agent | Custom agentic tool-calling loop (direct Ollama API, no CrewAI/litellm dependency) |
| Governor — Advisor | Ollama, `qwen2.5-coder:7b-instruct-q4_0` |
| Governor — Supervisor | Ollama, `deepseek-r1:8b` |
| Governor — policy engine | Open Policy Agent (Rego), Dockerized |
| Pattern Auditor | SQLite + local LLM-based action classifier (normalizes wording into fixed categories) |
| Backend | FastAPI, API-key authenticated |
| Evaluation | Custom jailbreak + OPA robustness test harnesses |

## Project Status: v1.1

Complete and evaluated:
- [x] Sandboxed Docker target
- [x] Red Agent + autonomous Adversarial Planning Agent
- [x] Custom agentic Blue Agent (dependency-free, tool-calling, dual scenario: SQLi + RoguePlanet/CVE-2026-50656)
- [x] Two-tier Governor (Advisor + Supervisor), fully local
- [x] OPA deterministic policy enforcement (allowlist design, tested for gaps)
- [x] Pattern Auditor (cumulative-risk detection, category-normalized)
- [x] Backend API with authentication, tying the full pipeline together
- [x] Full local migration -- no hosted LLM APIs anywhere in the pipeline
- [x] Jailbreak evaluation, OPA robustness evaluation, two-tier comparison, all with quantified results

Known limitations (documented, not hidden):
- Running the full pipeline concurrently with Docker + browser + IDE on CPU-only, memory-constrained hardware can exceed practical response times for the Supervisor tier (fails safe to escalate when this happens)
- Pattern Auditor uses fixed thresholds, which a determined attacker aware of the exact values could potentially probe around; production would need adaptive/statistical detection
- No log-source integrity verification yet (Blue Agent trusts log content as given)
- No tamper protection on the SQLite audit trail

Planned for future versions:
- [ ] Frontend dashboard (live action queue, audit trail viewer, attack simulation trigger)
- [ ] Log injection / data-source manipulation testing (extending the jailbreak evaluation methodology)
- [ ] Observability tracing (Arize Phoenix) for full agent-hop visibility
- [ ] Migration from SQLite to PostgreSQL
- [ ] Audit trail integrity (append-only or signed records)

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