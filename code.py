import time
import board
import busio
import adafruit_ahtx0
# import adafruit_veml7700

from os import getenv
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import wifi
import socketpool

sensor_desc = getenv("SENSOR_LOCATION")

sensors = [
    ("Temperature", "temp", "°C", "temperature"),
    ("Humidity", "hum", "%", "humidity"),
]

state_topics = dict()


# Define callback methods which are called when events occur
def connect(mqtt_client, userdata, flags, rc):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker!")
    print(f"Flags: {flags}\n RC: {rc}")

    for sen in sensors:
        name, id, unit, dc = sen
        state_topic = f"homeassistant/sensor/{sensor_desc.lower()}_th/{id}"
        state_topics[id] = state_topic
        config_template = f"""{{
        "name": "{sensor_desc} {name}",
        "state_topic": "{state_topic}",
        "unit_of_measurement": "{unit}",
        "device_class": "{dc}",
        "value_template": "{{{{ value | float }}}}",
        "unique_id": "{sensor_desc.lower()}_sensor_{id}",
        "device": {{
            "identifiers": [
            "pico_th_001"
            ],
            "name": "THL Sensor",
            "model": "Pi Pico W with AHT20",
            "manufacturer": "Moink Labs",
            "sw_version": "1.0"
        }}
        }}
        """
        # Pubish a retained config message
        mqtt_client.publish(state_topic + "/config", config_template, retain=True)


def disconnect(mqtt_client, userdata, rc):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    print("Disconnected from MQTT Broker!")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    # This method is called when the mqtt_client subscribes to a new feed.
    print(f"Subscribed to {topic} with QOS level {granted_qos}")


def unsubscribe(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client unsubscribes from a feed.
    print(f"Unsubscribed from {topic} with PID {pid}")


def publish(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client publishes data to a feed.
    print(f"Published to {topic} with PID {pid}")


def message(client, topic, message):
    print(f"New message on topic {topic}: {message}")


ssid = getenv("CIRCUITPY_WIFI_SSID")
ssid_connection_info = getenv("CIRCUITPY_WIFI_PASSWORD")
ha_username = getenv("HA_USERNAME")
ha_key = getenv("HA_KEY")

try:
    wifi.radio.connect(ssid, ssid_connection_info)
except TypeError:
    print("Could not find Wifi.")
    raise

pool = socketpool.SocketPool(wifi.radio)
print("My MAC addr: ", [hex(i) for i in wifi.radio.mac_address])
print(f"My IP address is {wifi.radio.ipv4_address}")
mqtt_client = MQTT.MQTT(
    broker="homeassistant.local",
    username=ha_username,
    password=ha_key,
    socket_pool=pool,
    port=1883,
)
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_publish = publish
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_message = message

i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
# veml7700 = adafruit_veml7700.VEML7700(i2c)
aht20 = adafruit_ahtx0.AHTx0(i2c)

mqtt_client.connect()

while True:
    print("tempC: %0.1f C" % aht20.temperature)
    print("rh: %0.1f %%" % aht20.relative_humidity)
    # print("lux: %d" % veml7700.autolux)

    mqtt_client.publish(state_topics["temp"], aht20.temperature)
    mqtt_client.publish(state_topics["hum"], aht20.relative_humidity)
    # mqtt_client.publish(state_topics["lux"], veml7700.autolux)

    # veml7700.wait_autolux(30)
    time.sleep(60)
