#!/usr/bin/env python3
import os
import sys
import requests
import json

# -----------------------
# Config
# -----------------------
TOKEN_FILE = "/config/tokens/rently_access_token.txt"  # can be Bearer or raw
LOGIN_URL  = "https://remotapp.rently.com/oauth/token"

# Your lock device (change if needed)
LOCK_DEVICE_ID = "697fdcc6-0a3b-4fa5-bf09-598ee2bfbb3b"
LOCK_URL = f"https://app2.keyless.rocks/api/devices/{LOCK_DEVICE_ID}"

def die(msg: str) -> None:
    print(msg)
    raise SystemExit(1)

def read_token() -> str:
    if os.path.exists(TOKEN_FILE):
        t = open(TOKEN_FILE, "r", encoding="utf-8").read().strip()
        if t:
            return t
    return ""

def write_token(raw: str) -> None:
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    # store Bearer form by default (works fine for you)
    if raw.lower().startswith("bearer "):
        val = raw
    else:
        val = "Bearer " + raw
    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        f.write(val)

def login() -> str:
    email = os.environ.get("RENTLY_EMAIL", "").strip()
    password = os.environ.get("RENTLY_PASSWORD", "").strip()
    if not email or not password:
        die("Missing RENTLY_EMAIL / RENTLY_PASSWORD env vars (needed for login).")

    r = requests.post(
        LOGIN_URL,
        headers={"Content-Type": "application/json"},
        json={"email": email, "password": password},
        timeout=20,
    )
    if not r.ok:
        die(f"LOGIN FAILED {r.status_code}: {r.text[:400]}")

    try:
        data = r.json()
    except Exception:
        die(f"LOGIN returned non-JSON: {r.text[:400]}")

    raw = (data.get("access_token") or "").strip()
    if not raw:
        die(f"LOGIN FAILED: no access_token in response: {json.dumps(data)[:400]}")

    write_token(raw)
    return read_token()

def put_unlock(auth_value: str) -> requests.Response:
    headers = {
        "Authorization": auth_value,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"commands": {"mode": "unlock"}}
    return requests.put(LOCK_URL, headers=headers, json=payload, timeout=20)

def main() -> None:
    auth_value = read_token()
    if not auth_value:
        auth_value = login()

    r = put_unlock(auth_value)
    if r.status_code in (401, 403):
        auth_value = login()
        r = put_unlock(auth_value)

    if not r.ok:
        die(f"UNLOCK FAILED {r.status_code}: {r.text[:500]}")

    print("Door unlock sent OK")

if __name__ == "__main__":
    main()
