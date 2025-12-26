#!/usr/bin/env python3
import os
import requests

RENTLY_TOKEN_FILE = "/config/tokens/rently_access_token.txt"
HA_TOKEN_FILE     = "/config/tokens/ha_token.txt"

DEVICE_ID  = "01d1355d-97a6-4215-b1a9-03c31741e51e"
DEVICE_URL = f"https://app2.keyless.rocks/api/devices/{DEVICE_ID}"

HA_BASE = "http://127.0.0.1:8123"

ENT_SYNCING = "input_boolean.rently_syncing"
ENT_MODE    = "input_select.rently_thermostat_mode"
ENT_SETPT   = "input_number.rently_thermostat_setpoint"
ENT_CURTEMP = "input_number.rently_current_temp"

def die(msg: str):
    print(msg)
    raise SystemExit(1)

def read_file(path: str) -> str:
    if not os.path.exists(path):
        die(f"Missing file: {path}")
    v = open(path, "r", encoding="utf-8").read().strip()
    if not v:
        die(f"Empty file: {path}")
    return v

def ha_call(service: str, data: dict):
    ha_token = read_file(HA_TOKEN_FILE)
    url = f"{HA_BASE}/api/services/{service}"
    headers = {"Authorization": f"Bearer {ha_token}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=data, timeout=20)
    if not r.ok:
        die(f"HA service {service} failed: {r.status_code} {r.text[:300]}")

def set_syncing(on: bool):
    ha_call("input_boolean/turn_on" if on else "input_boolean/turn_off", {"entity_id": ENT_SYNCING})

def set_input_number(entity_id: str, value: float):
    ha_call("input_number/set_value", {"entity_id": entity_id, "value": float(value)})

def set_input_select(entity_id: str, option: str):
    ha_call("input_select/select_option", {"entity_id": entity_id, "option": option})

def main():
    rently_token = read_file(RENTLY_TOKEN_FILE)

    r = requests.get(
        DEVICE_URL,
        headers={"Authorization": rently_token, "Accept": "application/json"},
        timeout=20,
    )
    if not r.ok:
        die(f"Rently GET failed: {r.status_code} {r.text[:400]}")
    data = r.json()

    status = data.get("status") or {}
    mode = (status.get("mode") or "").lower().strip()
    room_temp = status.get("room_temp")

    cool_sp = status.get("cooling_setpoint")
    heat_sp = status.get("heating_setpoint")

    if mode not in ("cool", "heat", "off"):
        die(f"Unexpected mode from device: {mode!r}")

    if room_temp is None:
        die("Missing status.room_temp")

    # Convert Celsius-looking values to F (rare, but safe)
    def to_f(x):
        x = float(x)
        return (x * 9.0 / 5.0) + 32.0 if -10 <= x <= 45 else x

    room_f = to_f(room_temp)

    # Choose which setpoint to mirror into your single HA helper
    target = None
    if mode == "cool" and cool_sp is not None:
        target = float(cool_sp)
    elif mode == "heat" and heat_sp is not None:
        target = float(heat_sp)
    # if mode is off, we keep existing setpoint helper unchanged (so it doesn't jump)

    set_syncing(True)
    try:
        set_input_number(ENT_CURTEMP, room_f)
        set_input_select(ENT_MODE, mode)
        if target is not None:
            set_input_number(ENT_SETPT, target)
    finally:
        set_syncing(False)

    print(f"Synced: mode={mode}, room_temp={room_f}, setpoint={(target if target is not None else 'unchanged')}")

if __name__ == "__main__":
    main()
