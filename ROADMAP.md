# Roadmap

## Done (v1.3)
- [x] Sandboxed Docker target (DVWA + OPA)
- [x] Red Agent + autonomous Adversarial Planning Agent
- [x] Custom, dependency-free Blue Agent (dual scenario: SQLi + RoguePlanet/CVE-2026-50656)
- [x] Two-tier Governor (Advisor + Supervisor), fully local via Ollama
- [x] OPA deterministic policy enforcement — allowlist design, gap-tested (0/6)
- [x] Pattern Auditor — category-normalized cumulative-risk detection
- [x] Detection Auditor — deterministic backstop for the Blue Agent
- [x] Hash-chained, tamper-evident audit trail
- [x] Backend API with authentication
- [x] Frontend dashboard + public-facing site
- [x] Full local migration — zero hosted LLM API calls anywhere
- [x] Jailbreak, OPA robustness, log injection, and tamper-detection evaluations, all with real quantified results

## Next up

| Item | Why |
|---|---|
| Escalation workflow / human review queue | "Escalate" is currently a data label with no interface for a human to act on it |
| Adaptive Pattern Auditor thresholds | Fixed thresholds can be probed and evaded by an attacker who learns the exact values |
| Log source authenticity verification | The Blue Agent currently trusts log content as given, with no origin verification |
| Append-only / signed audit storage | Current hash-chaining is tamper-*evident*, not tamper-*proof* |
| GPU-accelerated inference | Supervisor tier currently takes 2-5+ minutes on CPU-only hardware |
| Expanded evaluation suite | More test cases, broader attack-type coverage beyond SQLi/RoguePlanet |
| Observability tracing (e.g. Arize Phoenix) | Full visibility into every agent hop during a pipeline run |

## Explicitly not planned
**Comprehensive threat detection.** ThresholdGuard is a governance layer, not a detection engine — it evaluates whether a proposed action is safe to execute, regardless of what detected the underlying threat. Detection breadth is a separate problem already addressed by dedicated SIEM/EDR products. See the FAQ (wiki) for the full reasoning.