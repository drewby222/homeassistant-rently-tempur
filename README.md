# Home Assistant – Rently + Tempur / Sleeptracker

This repository provides working Home Assistant packages for:

- Rently thermostat + door lock
- Tempur / Sleeptracker adjustable base (flat, memory, massage levels)

The integrations are independent.
You may install either one or both.

No custom Home Assistant components are required.
Everything is YAML + Python scripts.

--------------------------------------------------
WHAT YOU GET
--------------------------------------------------

RENTLY
- Thermostat control (heat / cool / off)
- Setpoint control
- Door unlock
- Status sync (wall-unit changes show in HomeKit / HA)
- Loop-safe syncing (no automation feedback loops)

TEMPUR / SLEEPTRACKER
- Flat
- Memory 1
- Massage (off / level 1 / level 2)
- Left + right sides kept in sync
- Token refresh handled automatically

--------------------------------------------------
REQUIREMENTS
--------------------------------------------------

- Home Assistant (Container or OS)
- Ability to edit configuration.yaml
- Ability to copy files into:
  - /config/packages/
  - /config/python_scripts/
- Restart Home Assistant

--------------------------------------------------
IMPORTANT: TOKENS & PROXIES
--------------------------------------------------

TEMPUR / SLEEPTRACKER TOKEN CAPTURE

Sleeptracker does NOT provide a public API.

To obtain the INITIAL token, you must:
- Use an HTTPS proxy (Proxyman, Charles, mitmproxy, etc.)
- Capture traffic from the Sleeptracker iOS app
- Extract the Bearer token

IMPORTANT:
- This is required ONE TIME ONLY
- No proxy is needed after setup
- No proxy is needed for Rently

Once the token is stored, Home Assistant handles refresh automatically.

--------------------------------------------------
INSTALLATION (RECOMMENDED METHOD)
--------------------------------------------------

This repository uses Home Assistant Packages.
It does NOT interfere with existing configurations.

--------------------------------------------------
STEP 1 — ENABLE PACKAGES (ONE TIME)
--------------------------------------------------

Edit your EXISTING configuration.yaml and add:

homeassistant:
  packages: !include_dir_named packages

If homeassistant: already exists, merge this line.
Do NOT duplicate the homeassistant: key.

--------------------------------------------------
STEP 2 — COPY FILES
--------------------------------------------------

FROM THIS REPO:

packages/
  rently.yaml
  tempur_sleeptracker.yaml

COPY TO:

/config/packages/

You may copy only one if desired.

--------------------------------

python_scripts/
  rently_thermostat.py
  rently_get_temperature.py
  rently_login_and_unlock.py
  rently_refresh.py
  rently_sync_status.py

COPY TO:

/config/python_scripts/

--------------------------------------------------
STEP 3 — SECRETS
--------------------------------------------------

Copy:

secrets.example.yaml

Rename to:

secrets.yaml

Fill in values:

RENTLY
rently_email: "your@email.com"
rently_password: "yourpassword"

SLEEPTRACKER
sleeptracker_basic: "Basic BASE64_ENCODED_EMAIL:PASSWORD"

IMPORTANT:
- This is NOT the Bearer token
- It is used only to fetch a session token automatically

--------------------------------------------------
STEP 4 — RESTART HOME ASSISTANT
--------------------------------------------------

Restart Home Assistant completely.

After restart:
- Rently thermostat appears immediately
- Tempur controls appear once token is valid

--------------------------------------------------
HOMEKIT NOTES
--------------------------------------------------

- Fully compatible with HomeKit
- All entities can be exposed normally
- State sync works both directions

--------------------------------------------------
TROUBLESHOOTING
--------------------------------------------------

RENTLY NOT SYNCING?
- Ensure input_boolean.rently_syncing exists
- Ensure rently_sync_status.py is present
- Default sync interval is ~15 seconds

TEMPUR 419 ERRORS?
- Token expired
- Session refresh will auto-fix
- Restart HA if needed

--------------------------------------------------
SECURITY NOTES
--------------------------------------------------

- No secrets are committed
- Tokens are stored locally only
- You are responsible for your API usage

--------------------------------------------------
DISCLAIMER
--------------------------------------------------

These integrations rely on unofficial APIs.
They may break if vendors change endpoints.

Use at your own risk.

--------------------------------------------------
CREDITS
--------------------------------------------------

Created by Drew
Shared for personal and educational use
