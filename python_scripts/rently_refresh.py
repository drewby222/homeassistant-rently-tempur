#!/usr/bin/env python3
import os
import requests

EMAIL = os.environ.get("RENTLY_EMAIL", "").strip()
PASSWORD = os.environ.get("RENTLY_PASSWORD", "").strip()

ACCESS_TOKEN_RAW_FILE = "/config/tokens/rently_access_token_raw.txt"
ACCESS_TOKEN_BEARER_FILE = "/config/tokens/rently_access_token.txt"  # keep your existing path

os.makedirs("/config/tokens", exist_ok=True)

def die(msg):
    print(msg)
    raise SystemExit(1)

if not EMAIL or not PASSWORD:
    die("Missing env vars RENTLY_EMAIL / RENTLY_PASSWORD")

url = "https://remotapp.rently.com/oauth/token"
payload = {"email": EMAIL, "password": PASSWORD}
headers = {"Content-Type": "application/json"}

try:
    r = requests.post(url, json=payload, headers=headers, timeout=20)
except Exception as e:
    die(f"Error connecting to Rently token endpoint: {e}")

if not r.ok:
    die(f"Failed to fetch token: {r.status_code} {r.text}")

data = r.json()
access_token = (data.get("access_token") or "").strip()
if not access_token:
    die(f"No access_token returned: {data}")

with open(ACCESS_TOKEN_RAW_FILE, "w") as f:
    f.write(access_token)

with open(ACCESS_TOKEN_BEARER_FILE, "w") as f:
    f.write("Bearer " + access_token)

print(f"Saved raw token -> {ACCESS_TOKEN_RAW_FILE}")
print(f"Saved bearer token -> {ACCESS_TOKEN_BEARER_FILE}")
