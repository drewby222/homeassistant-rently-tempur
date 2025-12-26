# Home Assistant: Rently + Sleeptracker/Tempur bundle

## What this is
A working HA configuration + scripts that:
- Controls Rently thermostat (and syncs status back so wall-unit changes show in HA/HomeKit)
- Controls Tempur/Sleeptracker adjustable base (memory/flat/massage level logic)
- Uses a sync-guard (input_boolean.rently_syncing) to prevent automation feedback loops

## Files
- configuration.yaml
- python_scripts/
- secrets.example.yaml (rename to secrets.yaml and fill in)

## Install (general)
1) Copy `python_scripts/` to your HA config dir (usually `/config/python_scripts/`)
2) Merge/replace `configuration.yaml` as desired
3) Create `secrets.yaml` from `secrets.example.yaml`
4) Restart Home Assistant

## Notes
- Fast polling is set in automations (seconds-based). Adjust if rate-limited.
