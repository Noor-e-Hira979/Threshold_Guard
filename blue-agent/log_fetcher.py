"""
log_fetcher.py
Pulls raw Apache access logs from the sandboxed DVWA container.
This is what the Blue Agent analyzes to detect malicious behavior --
it works purely from logs, not from any direct signal sent by the Red Agent,
to reflect a realistic detection scenario.
"""

import subprocess

CONTAINER_NAME = "thresholdguard-target"
ACCESS_LOG_PATH = "/var/log/apache2/access.log"


def fetch_access_logs(lines: int = 50) -> list[str]:
    """
    Runs `docker exec` to read the last N lines of the container's Apache
    access log. Returns a list of raw log lines.
    """
    try:
        result = subprocess.run(
            ["docker", "exec", CONTAINER_NAME, "tail", "-n", str(lines), ACCESS_LOG_PATH],
            capture_output=True,
            text=True,
            check=True,
        )
        log_lines = [line for line in result.stdout.splitlines() if line.strip()]
        return log_lines
    except subprocess.CalledProcessError as e:
        print(f"[!] Failed to fetch logs from container '{CONTAINER_NAME}': {e.stderr}")
        return []


if __name__ == "__main__":
    logs = fetch_access_logs()
    print(f"[+] Retrieved {len(logs)} log lines:\n")
    for line in logs:
        print(line)