"""
dvwa_session.py
Handles authentication and session management for DVWA (Damn Vulnerable Web App).
This is a prerequisite utility used by all Red Agent attack scripts.
"""

import requests
from bs4 import BeautifulSoup

DVWA_BASE_URL = "http://localhost:8080"


class DVWASession:
    def __init__(self, base_url: str = DVWA_BASE_URL, username: str = "admin", password: str = "password"):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self) -> bool:
        """Logs into DVWA and sets the security level to 'low'. Returns True on success."""
        login_page = self.session.get(f"{self.base_url}/login.php")
        soup = BeautifulSoup(login_page.text, "html.parser")
        token_input = soup.find("input", {"name": "user_token"})

        if token_input is None:
            print("[!] Could not find CSRF token on login page. Is DVWA running?")
            return False

        csrf_token = token_input["value"]

        payload = {
            "username": self.username,
            "password": self.password,
            "Login": "Login",
            "user_token": csrf_token,
        }
        resp = self.session.post(f"{self.base_url}/login.php", data=payload)

        if "login.php" in resp.url:
            print("[!] Login failed. Check credentials.")
            return False

        print("[+] Logged into DVWA successfully.")
        self._set_security_level("low")
        return True

    def _set_security_level(self, level: str = "low"):
        """Ensures DVWA security level matches what the attack scripts expect."""
        sec_page = self.session.get(f"{self.base_url}/security.php")
        soup = BeautifulSoup(sec_page.text, "html.parser")
        token_input = soup.find("input", {"name": "user_token"})
        csrf_token = token_input["value"] if token_input else ""

        payload = {
            "security": level,
            "seclev_submit": "Submit",
            "user_token": csrf_token,
        }
        self.session.post(f"{self.base_url}/security.php", data=payload)
        print(f"[+] Security level set to '{level}'.")

    def get(self, path: str, params: dict = None):
        return self.session.get(f"{self.base_url}{path}", params=params)


if __name__ == "__main__":
    dvwa = DVWASession()
    dvwa.login()