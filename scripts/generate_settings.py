import sys
from pathlib import Path

template_path = Path(sys.argv[1])
output_path = Path(sys.argv[2])

if output_path.exists():
    print("settings.toml already exists. Skipping.")
    sys.exit(0)

values = {
    "WIFI_SSID": input("WiFi SSID: "),
    "WIFI_PASSWORD": input("WiFi Password: "),
    "HA_USERNAME": input("Home Assistant MQTT Username: "),
    "HA_KEY": input("Home Assistant MQTT Password: "),
    "SENSOR_LOCATION": input("Sensor location (e.g. Office): "),
}

template = template_path.read_text()
filled = template.format(**values)

output_path.write_text(filled)
print(f"Generated settings.toml to {output_path}")
