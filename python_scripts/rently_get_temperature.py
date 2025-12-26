#!/usr/bin/env python3
import os
import requests

RENTLY_TOKEN_FILE = "/config/tokens/rently_access_token.txt"  # Bearer or raw (both work for you)
HA_TOKEN_FILE     = "/config/tokens/ha_token.txt"

DEVICE_ID  = "01d1355d-97a6-4215-b1a9-03c31741e51e"
DEVICE_URL = f"https://app2.keyless.rocks/api/devices/{DEVICE_ID}"

HA_BASE        = "http://127.0.0.1:8123"
HA_TEMP_ENTITY = "input_number.rently_current_temp"

def die(msg: str) -> None:
    print(msg)
    raise SystemExit(1)

def read_file(path: str) -> str:
    if not os.path.exists(path):
        die(f"Missing file: {path}")
    val = open(path, "r", encoding="utf-8").read().strip()
    if not val:
        die(f"Empty file: {path}")
    return val

def ha_set_input_number(ha_token: str, value: float) -> None:
    url = f"{HA_BASE}/api/services/input_number/set_value"
    headers = {
        "Authorization": f"Bearer {ha_token}",
        "Content-Type": "application/json",
    }
    payload = {"entity_id": HA_TEMP_ENTITY, "value": float(value)}
    r = requests.post(url, headers=headers, json=payload, timeout=20)
    if not r.ok:
        die(f"HA set_value failed: {r.status_code} {r.text[:500]}")

def main() -> None:
    rently_token = read_file(RENTLY_TOKEN_FILE)
    ha_token     = read_file(HA_TOKEN_FILE)

    try:
        r = requests.get(
            DEVICE_URL,
            headers={"Authorization": rently_token, "Accept": "application/json"},
            timeout=20,
        )
    except Exception as e:
        die(f"Rently GET failed: {e}")

    if not r.ok:
        die(f"Rently GET {DEVICE_URL} -> {r.status_code} {r.text[:500]}")

    try:
        data = r.json()
    except Exception:
        die(f"Rently returned non-JSON: {r.text[:500]}")

    # Deterministic field you discovered:
    try:
        temp = float(data["status"]["room_temp"])
    except Exception:
        die("Missing expected field: status.room_temp")

    # Optional: handle Celsius just in case (unlikely for US thermostat)
    if -10 <= temp <= 45:
        used = (temp * 9.0 / 5.0) + 32.0
        note = "C->F"
    else:
        used = temp
        note = "F"

    ha_set_input_number(ha_token, used)
    print(f"Read status.room_temp={temp} ({note}); wrote {used} -> {HA_TEMP_ENTITY}")

if __name__ == "__main__":
    main()
