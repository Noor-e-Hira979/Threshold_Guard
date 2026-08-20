# Problem Statement

## Problem
As organizations adopt autonomous AI agents for security detection and incident response, nobody has solved how much autonomy is actually safe to grant those agents. Give an agent too much authority and one wrong action can cascade into an outage or a breach; give it too little and security teams remain stuck in the exact alert-fatigue, slow-response bottleneck that autonomous agents were introduced to fix. This is a governance gap, not a detection gap — most current effort in the industry goes toward detecting threats faster, not toward deciding whether an AI's proposed response to a threat is trustworthy enough to execute without a human in the loop.

## Target Users
- **Security Operations Center (SOC) teams** at mid-to-large organizations already using or piloting autonomous detection/response tooling (SIEM, EDR, or custom agentic systems)
- **Platform/security engineering teams** building in-house agentic security automation, who need a safety layer they can drop into an existing pipeline rather than build from scratch
- **Security tool vendors** (like MSSPs or SOC automation platforms) who want to offer "safe autonomy" as a feature, not just faster detection

## Current Workflow
1. A detection system (SIEM, EDR, or an AI agent) identifies suspicious activity
2. It either (a) generates an alert and waits for a human analyst to manually investigate and act, or (b) is configured to auto-remediate directly, with no independent check on whether that specific action is safe
3. In case (a), analysts face constant alert fatigue — most alerts are false positives, real threats get buried, and response is slow
4. In case (b), the organization is trusting the detection/response agent's judgment completely, with no safeguard against the agent (or its underlying AI) being wrong, manipulated, or exploited via a sequence of individually-small actions

## Existing Solutions & Their Limitations
Current "agentic AI security" products (autonomous SOC platforms, AI-driven auto-remediation tools) focus on making detection and response *faster* and *more automated* — this is the well-funded, actively competitive part of the market. What they do not address:

- **No independent judgment layer between AI reasoning and action execution.** If the detecting/responding AI is fooled (via prompt injection, manipulated data, or simple model error), most systems have no separate mechanism to catch that before the action executes.
- **No defense against decomposed/evasive harmful actions.** A single-action risk check can be defeated by splitting one large harmful action into many small, individually-approved ones — a known evasion pattern (analogous to financial transaction "structuring") that most tools do not check for.
- **Detection failures are often silent.** If the AI reasoning behind detection itself is manipulated into under-reporting a threat, there may be no proposed action at all for any downstream safety check to evaluate — the failure produces no signal.

## Opportunity
Build a governance layer, not another detection engine — one that any organization's existing detection/response tooling can sit behind. The opportunity is in the layer nobody is building: independent, non-LLM-dependent verification of whether an AI-proposed security action is safe to execute autonomously, with specific defenses against the failure modes above (LLM manipulation, cumulative/decomposed evasion, and silent detection failure).

## Why AI (and why not *only* AI)
AI reasoning is genuinely useful here — a fast LLM-based advisor can explain *why* an action looks risky in plain language, which a purely rule-based system cannot do on its own, and a second, stronger LLM tier can catch reasoning errors the first misses. But AI alone cannot be the safety guarantee, because any LLM is theoretically manipulable via adversarial input. The system is designed so the actual binding decision is made deterministically (via a policy engine, not an LLM) — AI improves the *quality and explainability* of the decision, while a non-AI layer guarantees its *reliability*.

## Expected Impact
- **For SOC teams:** fewer false all-clear signals from manipulated or mistaken automation, without reintroducing the manual-review bottleneck for genuinely low-risk actions
- **For organizations adopting agentic security tools:** a concrete, testable answer to "how do we know this AI won't do something catastrophic," backed by adversarial evaluation data rather than a vendor's assurance
- **For the broader field:** a demonstrated, evaluated pattern (multi-tier AI review + deterministic policy backstop + cumulative-pattern detection) that other agentic systems — security or otherwise — can adopt as autonomy expands faster than governance currently does