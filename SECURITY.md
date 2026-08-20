# Security Policy

## Reporting a Vulnerability
If you find a security issue in ThresholdGuard itself (not in DVWA, which is intentionally vulnerable by design), please report it privately rather than opening a public issue — open a GitHub issue marked `[SECURITY]` with minimal public detail, or contact the maintainer directly, and full details can be shared privately. Please allow time to investigate and patch before any public disclosure.

## Scope

**In scope:**
- The Governor (Advisor, Supervisor, OPA policy logic)
- The Pattern Auditor and its hash-chain integrity mechanism
- The Detection Auditor
- The Backend API and its authentication
- Any bypass of ThresholdGuard's own governance decisions

**Out of scope:**
- DVWA (`vulnerables/web-dvwa`) — this is a deliberately vulnerable application used as a sandboxed test target, not part of ThresholdGuard's own codebase
- Vulnerabilities in third-party dependencies (Ollama, Docker, OPA) — report these to their respective maintainers

## Known, Documented Limitations
These are not secret — they're tracked openly in `TESTING.md` and the wiki's Security Considerations page:
- No verification of the identity of the agent/system submitting a proposed action to the API (only a shared API key)
- Pattern Auditor uses fixed, known detection thresholds
- No log-source authenticity verification
- Audit trail is tamper-*evident* (hash-chained), not tamper-*proof* — a party with direct database access could still alter records, though doing so would be detectable

If you find a way to exploit any of the above beyond what's already documented, or find something not listed here, please report it.

## Supported Versions
This is an actively developed prototype (currently v1.2). Security fixes are applied to the latest version only; there is no long-term support branch at this stage.