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


# ensure_wifi attempts to reconnect using the specified credentials when connectivity is lost
def ensure_wifi():
    # TODO: Verify whether this pool needs to be recreated each time
    pool = socketpool.SocketPool(wifi.radio)

    while True:
        ssid = getenv("CIRCUITPY_WIFI_SSID")
        ssid_connection_info = getenv("CIRCUITPY_WIFI_PASSWORD")

        # try and connect
        try:
            wifi.radio.connect(ssid, ssid_connection_info)
        except TypeError:
            print("Could not find Wifi.")
            raise

        # if unsuccessful, retry with backoff
        if not wifi.radio.connected:
            print("error connecting to wifi, retrying...")
            time.sleep(9)
            continue

        print("My MAC addr: ", [hex(i) for i in wifi.radio.mac_address])
        print(f"My IP address is {wifi.radio.ipv4_address}")

        # if successful, ensure_mqtt
        ensure_mqtt(pool)


# ensure_mqtt attempts to reconnect to the mqtt server and publish data to the relevant topics
def ensure_mqtt(pool):
    while True:
        ha_username = getenv("HA_USERNAME")
        ha_key = getenv("HA_KEY")

        # try and connect
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

        mqtt_client.connect()

        # if unsuccessful, assume the issue is with the wifi
        if not mqtt_client.is_connected():
            print("error connecting to MQTT server")
            return

        # if successful, run temperature loop
        publish_readings(mqtt_client)


# publish_readings reads from the relevant sensors and
def publish_readings(mqtt_client):
    while True:
        print("tempC: %0.1f C" % aht20.temperature)
        print("rh: %0.1f %%" % aht20.relative_humidity)
        # print("lux: %d" % veml7700.autolux)

        if not mqtt_client.is_connected():
            print("MQTT connection broken, retrying...")
            break

        mqtt_client.publish(state_topics["temp"], aht20.temperature)
        mqtt_client.publish(state_topics["hum"], aht20.relative_humidity)
        # mqtt_client.publish(state_topics["lux"], veml7700.autolux)

        # veml7700.wait_autolux(30)
        time.sleep(60)


i2c = busio.I2C(scl=board.GP1, sda=board.GP0)
# veml7700 = adafruit_veml7700.VEML7700(i2c)
aht20 = adafruit_ahtx0.AHTx0(i2c)

ensure_wifi()
