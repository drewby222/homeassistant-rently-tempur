#!/usr/bin/env python3
import os
import sys
import requests
import json
from typing import Optional

ARG_LOG = "/config/rently_thermostat_args.log"

TOKEN_FILE = "/config/tokens/rently_access_token.txt"       # may be raw or "Bearer ..."
TOKEN_RAW_FILE = "/config/tokens/rently_access_token_raw.txt"  # optional, if present we prefer it

DEVICE_ID = "01d1355d-97a6-4215-b1a9-03c31741e51e"
API_URL = f"https://app2.keyless.rocks/api/devices/{DEVICE_ID}"
LOGIN_URL = "https://remotapp.rently.com/oauth/token"

def log_argv():
    try:
        with open(ARG_LOG, "a", encoding="utf-8") as f:
            f.write("ARGV=" + repr(sys.argv) + "\n")
    except Exception as e:
        print("ARG LOG FAIL:", e)

def die(msg: str) -> None:
    print(msg)
    raise SystemExit(1)

def read_file(path: str) -> str:
    if not os.path.exists(path):
        return ""
    return open(path, "r", encoding="utf-8").read().strip()

def write_file(path: str, data: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(data)

def normalize_auth(token_text: str) -> str:
    """
    Returns a string to use as the Authorization header value.
    Accepts either raw token or already-prefixed 'Bearer ...'.
    """
    t = (token_text or "").strip()
    if not t:
        return ""
    if t.lower().startswith("bearer "):
        return t
    # Some endpoints accept raw, but Bearer is safer/standard
    return "Bearer " + t

def login_and_store() -> str:
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

    # Store both forms
    write_file(TOKEN_RAW_FILE, raw)
    write_file(TOKEN_FILE, "Bearer " + raw)
    return "Bearer " + raw

def get_auth_header() -> str:
    # Prefer raw file if present, but normalize either way
    raw = read_file(TOKEN_RAW_FILE)
    if raw:
        return normalize_auth(raw)

    t = read_file(TOKEN_FILE)
    return normalize_auth(t)

def send_update(auth_value: str, commands: dict) -> requests.Response:
    headers = {
        "Authorization": auth_value,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"commands": commands}
    return requests.put(API_URL, headers=headers, json=payload, timeout=20)

def main() -> None:
    log_argv()

    if len(sys.argv) != 3:
        die("Usage: rently_thermostat.py <setpoint> <mode>")

    raw_temp = sys.argv[1]
    mode = sys.argv[2].lower().strip()

    if mode not in ("cool", "heat", "off"):
        die(f"Invalid mode: {mode}")

    commands = {"mode": mode}
    if mode != "off":
        try:
            setpoint = int(round(float(raw_temp)))
        except Exception:
            die(f"Invalid setpoint: {raw_temp}")
        commands["setpoint"] = setpoint

    auth_value = get_auth_header()
    if not auth_value:
        auth_value = login_and_store()

    # Try once with existing token, then login+retry on auth errors
    r = send_update(auth_value, commands)
    if r.status_code in (401, 403):
        auth_value = login_and_store()
        r = send_update(auth_value, commands)

    if not r.ok:
        die(f"UPDATE FAILED {r.status_code}: {r.text[:500]}")

    print("Thermostat updated:", {"commands": commands})

if __name__ == "__main__":
    main()
