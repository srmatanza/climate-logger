# Home Climate Logger

A CircuitPython-based climate logging system for the Raspberry Pi Pico W.
This project reads temperature and humidity using the AHT20 sensor
and publishes data to Home Assistant via MQTT.

---

## Prerequisites

- Raspberry Pi Pico W with CircuitPython installed
- Connected AHT20 sensor (I²C)
- [uv](https://pypi.org/project/uv/) installed for environment & dependency management
- [circup](https://pypi.org/project/circup/) for managing CircuitPython libraries

---

## Setup

### 1. Install development dependencies

```bash
uv sync --extra dev
```

This ensures you have circup and circuitpython-stubs available.

### 2. Fill out your settings

Copy settings.template.toml to settings.toml or use the deploy script to generate it.
Provide your credentials when prompted:

- Wi-Fi SSID — Wi-Fi network name
- Wi-Fi Password — shhh!
- HA_USERNAME — Home Assistant username that has access to MQTT
- HA_KEY — Home Assistant user's password

The deploy script will automatically write these to `settings.toml` on the Pico.

## Deployment

With your Pico W connected and mounted:

```bash
./deploy.sh
```

This script will:

1. Check that a CircuitPython device is connected
2. Generate settings.toml from the template (prompting for credentials)
3. Install or update CircuitPython libraries via circup
4. Copy code.py to the board

## Updating Code or Libraries

To update your CircuitPython libraries:

```bash
uv run --extra dev circup update
```
