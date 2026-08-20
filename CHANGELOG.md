# Changelog

All notable changes to ThresholdGuard are documented here.

## [1.2] — Local resilience, log injection defense, audit integrity, frontend

### Added
- `blue-agent/detection_auditor.py` — deterministic (non-LLM) signature-scan backstop for the Blue Agent, catching cases where log-content manipulation fools the LLM into under-reporting
- `evaluation/log_injection_test.py` — adversarial evaluation of log-content manipulation resistance
- Hash-chained audit trail (`prev_hash`/`record_hash` columns in `action_store.py`) with `verify_chain_integrity()`
- `evaluation/tamper_detection_test.py` — proves the hash-chain actually detects tampering
- Full React + Tailwind frontend: public landing page, animated pipeline architecture view, live investigation console with evidence-chain display, evaluation results showcase
- API key authentication on `/investigate`, `/audit-trail`, `/pattern-audit`
- `TESTING.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, and a 13-page GitHub wiki

### Fixed
- OPA scope-matching false-positive: substring match on `"all"` incorrectly matched inside words like `"firewall"` — replaced with regex word-boundary matching
- Pattern Auditor detection window recalibrated from 10 to 45 minutes to reflect real two-tier local-inference latency
- URL-encoded attack payloads (`+`, `%XX`) evading the Detection Auditor's regex — fixed with `unquote_plus` decoding before scanning

### Changed
- Blue Agent completely rewritten from CrewAI to a custom direct-Ollama tool-calling loop, permanently resolving a `litellm`/Ollama multi-turn tool-calling `IndexError`

---

## [1.1] — Full local migration, two-tier Governor

### Added
- `governor/supervisor.py` — second LLM tier (deepseek-r1:8b) that cross-checks the Advisor's reasoning for signs of manipulation
- `pattern-auditor/action_classifier.py` — LLM-based normalization of action wording into a fixed taxonomy, fixing exact-string-match brittleness in cumulative-pattern detection
- `evaluation/opa_robustness_test.py` — adversarial testing of OPA's own policy logic, independent of LLM manipulation

### Changed
- Migrated all LLM calls (Advisor, Blue Agent, classifier, Adversarial Planner, RoguePlanet generator) from hosted Groq API to local Ollama — no data leaves the machine
- OPA policy redesigned from a denylist (`never_auto_approve_types`) to an allowlist (`known_safe_auto_approve_types`), after robustness testing found the denylist auto-approved any unlisted action type by default

### Fixed
- Pattern Auditor false negative caused by two test scripts writing to different SQLite files (relative path resolved differently depending on working directory) — fixed with an absolute path

---

## [1.0] — Initial working pipeline

### Added
- Sandboxed Docker target (DVWA) + Open Policy Agent
- Red Agent (SQL injection against DVWA)
- Adversarial Planning Agent — autonomously reasons about splitting a harmful objective into evasive sub-actions
- Agentic Blue Agent (initially CrewAI-based) with dual detection scenarios: SQL injection and a simulated RoguePlanet (CVE-2026-50656) privilege-escalation scenario
- Governor: LLM Advisor (initially Groq-hosted) + OPA binding decision
- Pattern Auditor: SQLite-backed cumulative-risk detection across auto-approved actions
- FastAPI backend tying the full pipeline together
- `evaluation/jailbreak_test.py` — first adversarial evaluation, proving OPA catches dangerous actions even when the LLM Advisor is manipulated