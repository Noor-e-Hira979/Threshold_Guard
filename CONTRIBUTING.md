# Contributing to ThresholdGuard

## Setup
Follow `README.md`'s Setup section — you'll need Docker, Ollama (with `qwen2.5-coder:7b-instruct-q4_0` and `deepseek-r1:8b` pulled), and Python 3.11+.

## Before making changes
Read `TESTING.md` and the "Key engineering decisions" section of the wiki's Development page — several design choices (allowlist over denylist, custom Blue Agent instead of CrewAI, regex word-boundary matching) exist because testing found a real gap with the simpler approach. Don't revert these without re-running the relevant test in `evaluation/`.

## Adding a new module or feature
1. Add the standalone script first, testable on its own (`if __name__ == "__main__":` block)
2. Wire it into the pipeline only after it works standalone
3. If it touches safety/governance logic, add or extend an adversarial test in `evaluation/` before considering it done

## Code style
- Python: standard library + minimal dependencies where possible. Each module keeps its own `requirements.txt`.
- All LLM calls should go through local Ollama (`http://localhost:11434`) — no hosted API calls anywhere in the pipeline.
- Every LLM-calling function should fail safe (default to `escalate`/reject) on error or invalid output, not silently pass or default to approval.

## Testing
```
python evaluation/jailbreak_test.py
python evaluation/opa_robustness_test.py
python evaluation/log_injection_test.py
python evaluation/tamper_detection_test.py
```
If you change OPA policy logic, re-run `opa_robustness_test.py` and confirm no new gaps. If you change Governor/Advisor logic, re-run `jailbreak_test.py`.

## Commit messages
Keep them descriptive about *why*, not just *what* — e.g. `fix: regex word-boundary match for scope check (substring match false-matched "firewall")`, not `fix bug`.

## Questions
Open an issue, or check the wiki's FAQ page first.