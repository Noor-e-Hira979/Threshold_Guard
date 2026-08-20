# ThresholdGuard

An agentic AI security-governance system that decides how much autonomy to give AI agents during automated incident response. Instead of letting an autonomous agent execute security actions directly, ThresholdGuard places a two-tier LLM review and a deterministic policy engine between every proposed action and its execution — evaluating whether that action is safe to run autonomously, even if the AI reasoning behind it has been manipulated.

## The Problem

Autonomous security agents are increasingly expected to detect and remediate threats without waiting for a human — but nobody has solved how much autonomy is actually safe to hand them. Give an agent too much authority and one wrong action can cascade into an outage or a breach; give it too little and you're back to the alert-fatigue, slow-response problem autonomous agents were supposed to fix. This project treats that as the actual research question, rather than building another detection engine.

## Architecture

```
Red Agent / Adversarial Planning Agent
        │  attacks a sandboxed target; the adversarial
        │  agent autonomously reasons about how to split
        │  a harmful objective into evasive sub-actions
        ▼
Blue Agent (custom agentic tool-calling loop, local Ollama)
        │  investigates logs, proposes a remediation action
        ▼
Governor (two-tier, fully local via Ollama)
    ├── Advisor (qwen2.5-coder, fast)   → first-pass advisory risk assessment
    ├── Supervisor (deepseek-r1:8b)     → cross-checks the Advisor's reasoning
    │                                      for signs of manipulation
    └── OPA Policy (Rego)               → BINDING decision: auto_approve /
                                            escalate / block — unaffected
                                            by either LLM tier
        ▼
Pattern Auditor
        │  scans rolling history of auto-approved actions for
        │  cumulative-risk patterns (normalized by category, not
        │  raw wording) that no single-action check could see
        ▼
Backend API (FastAPI, API-key protected) → audit trail, investigation trigger
        ▼
Frontend (React + Tailwind) → live console, evidence-chain viewer, public site
```

**Core safety design:** neither LLM tier's verdict is ever authoritative. OPA's decision is final and cannot be overridden by prompt manipulation, because it isn't reasoning over language at all — it's evaluating hard, pre-defined rules (Rego policies). All LLM inference runs locally via Ollama; no data leaves the machine.

A **Detection Auditor** (deterministic signature scanner) also backstops the Blue Agent itself, since testing showed a manipulated Blue Agent can silently under-report threats — a more dangerous failure mode than a manipulated Advisor, since no downstream check ever sees a proposed action to evaluate.

## Evaluation Summary

Full methodology and data in `TESTING.md` and the wiki's Testing & Evaluation page.

| Test | Result |
|---|---|
| Jailbreak resistance (Advisor manipulation) | LLM fooled 1/4 (25%) — OPA caught 4/4 (100%) regardless |
| OPA policy robustness | 0/6 gaps after allowlist redesign + regex fix |
| Two-tier Supervisor | Weak model missed a manipulated verdict; strong model caught it |
| Log injection resistance | Blue Agent resisted 3/4 (75%); Detection Auditor backstop caught the rest |
| Cumulative evasion detection | Correctly flagged a non-scripted, autonomously-split 5-action sequence |
| Audit trail tamper detection | Deliberate tampering test correctly detected via hash-chain verification |

## Tech Stack

| Layer | Technology |
|---|---|
| Sandboxed target | DVWA (Docker) |
| Red / Adversarial agent | Custom Python + local Ollama LLM reasoning |
| Blue agent | Custom agentic tool-calling loop (direct Ollama API, no CrewAI/litellm dependency) |
| Governor — Advisor | Ollama, `qwen2.5-coder:7b-instruct-q4_0` |
| Governor — Supervisor | Ollama, `deepseek-r1:8b` |
| Governor — policy engine | Open Policy Agent (Rego), Dockerized |
| Pattern Auditor | SQLite + hash-chained audit trail + local LLM-based action classifier |
| Backend | FastAPI, API-key authenticated |
| Frontend | React + Vite + Tailwind CSS v4 |
| Evaluation | Custom jailbreak, OPA robustness, log injection, and tamper-detection test harnesses |

## Project Status: v1.2

Complete and evaluated:
- [x] Sandboxed Docker target
- [x] Red Agent + autonomous Adversarial Planning Agent
- [x] Custom agentic Blue Agent (dependency-free, tool-calling, dual scenario: SQLi + RoguePlanet/CVE-2026-50656)
- [x] Two-tier Governor (Advisor + Supervisor), fully local
- [x] OPA deterministic policy enforcement (allowlist design, tested for gaps)
- [x] Pattern Auditor (cumulative-risk detection, category-normalized)
- [x] Detection Auditor (deterministic backstop for the Blue Agent)
- [x] Hash-chained, tamper-evident audit trail
- [x] Backend API with authentication
- [x] Frontend dashboard + public-facing site
- [x] Full local migration — no hosted LLM APIs anywhere in the pipeline
- [x] Jailbreak, OPA robustness, log injection, and tamper-detection evaluations, all with quantified results

Known limitations (documented, not hidden — see `TESTING.md`):
- Running the full pipeline concurrently with Docker + browser + IDE on CPU-only, memory-constrained hardware can exceed practical response times for the Supervisor tier (fails safe to escalate when this happens)
- Pattern Auditor uses fixed thresholds, which a determined attacker aware of the exact values could potentially probe around
- No log-source authenticity verification yet (Blue Agent trusts log content as given)
- Audit trail is tamper-*evident*, not tamper-*proof* (hash-chaining detects modification after the fact, doesn't prevent it)

Planned for future versions:
- [ ] Escalation workflow / human-in-the-loop review queue
- [ ] Adaptive Pattern Auditor thresholds
- [ ] Log source authenticity verification
- [ ] Append-only or cryptographically signed audit storage
- [ ] GPU-accelerated inference for production-latency response times
- [ ] Observability tracing (Arize Phoenix) for full agent-hop visibility

## Setup

1. Pull local models and start Ollama:
   ```
   ollama pull qwen2.5-coder:7b-instruct-q4_0
   ollama pull deepseek-r1:8b
   ollama serve
   ```
2. Start the sandbox + policy engine:
   ```
   docker-compose up -d
   ```
3. Initialize DVWA: open `http://localhost:8080`, log in (`admin`/`password`), click **Create/Reset Database**, set **DVWA Security** to **Low**.
4. Install dependencies per-module (`pip install -r <module>/requirements.txt --break-system-packages`).
5. Set `THRESHOLDGUARD_API_KEY` in `backend/.env`.
6. Run the backend: `cd backend && uvicorn main:app --reload --port 8000`
7. Run the frontend: `cd frontend && npm install && npm run dev`

## Repo Structure

```
thresholdguard/
├── docker-compose.yml
├── red-agent/           # Red Agent + Adversarial Planning Agent + RoguePlanet log generator
├── blue-agent/           # Custom agentic detection + Detection Auditor backstop
├── governor/               # Advisor + Supervisor + OPA client + policies
│   └── opa-policies/
├── pattern-auditor/          # Cumulative-risk detection + hash-chained audit trail
├── backend/                    # FastAPI orchestration layer
├── evaluation/                   # Jailbreak, OPA robustness, log injection, tamper-detection tests
├── frontend/                       # React dashboard + public site
├── TESTING.md                        # Full evaluation methodology and results
└── README.md
```

## Documentation

Full project documentation lives in the GitHub Wiki: Problem, Solution, Architecture, Agent Design, Tools & Tech Stack, Installation, Usage, Development, Testing & Evaluation, Security Considerations, Roadmap, and FAQ.