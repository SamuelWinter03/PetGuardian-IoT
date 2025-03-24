import time
import json
import os
import random
import paho.mqtt.client as mqtt

# Try to import Raspberry Pi GPIO library
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    REAL_SENSOR = True
except ImportError:
    print("GPIO module not found! Running in virtual mode...")
    REAL_SENSOR = False

# Azure IoT Hub connection string
CONNECTION_STRING = "HostName=IoTPawTrack.azure-devices.net;DeviceId=collar01;SharedAccessKey=ShzFs2jgI06rAjksNrEst8Byb8x2ljbHrBGYT+raQ1E="

from azure.iot.device import IoTHubDeviceClient, Message

# Configuration
SENSOR_PIN = 17  # GPIO pin to simulate light detection (e.g., button or photodiode)
BROKER = "broker.hivemq.com"
TOPIC = "petguardian/light"

# Setup GPIO pin if using physical sensor
if REAL_SENSOR:
    GPIO.setup(SENSOR_PIN, GPIO.IN)

def send_data_to_cloud(light_data):
    """Send light sensor data to MQTT broker."""
    client = mqtt.Client()
    try:
        client.connect(BROKER, port=1883, keepalive=60)
        payload = json.dumps({
            "deviceId": "collar01",  # MUST match what Cosmos routing expects
            "sensor": "led_light_sensor" if REAL_SENSOR else "simulated_led_light",
            "lux": light_data["lux"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        client.publish(TOPIC, payload)
        print(f"✅ Sent Light Data to MQTT Broker: {payload}")
    except Exception as e:
        print(f"❌ Failed to connect to MQTT broker: {e}")
    finally:
        client.disconnect()

def send_data_to_azure(light_data):
    """Send light sensor data to Azure IoT Hub."""
    try:
        client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
        payload = json.dumps({
            "deviceId": "collar01",  # MUST match what Cosmos routing expects
            "sensor": "led_light_sensor" if REAL_SENSOR else "simulated_led_light",
            "lux": light_data["lux"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        message = Message(payload)
        client.send_message(message)
        print(f"✅ Sent Light Data to Azure IoT Hub: {payload}")
        client.disconnect()
    except Exception as e:
        print(f"❌ Failed to send data to Azure IoT Hub: {e}")

def log_light_data(light_data):
    """Logs light sensor data into a JSON file."""
    log_entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "lux": light_data["lux"]
    }

    if os.path.exists("light_log.json"):
        try:
            with open("light_log.json", "r") as log_file:
                logs = json.load(log_file)
            if not isinstance(logs, list):
                logs = []
        except (json.JSONDecodeError, FileNotFoundError):
            logs = []
    else:
        logs = []

    logs.append(log_entry)

    with open("light_log.json", "w") as log_file:
        json.dump(logs, log_file, indent=4)

    print(f"📝 Logged Light Data: {log_entry}")

def get_light_level():
    """Gets light level from physical sensor or simulates it."""
    if REAL_SENSOR:
        if GPIO.input(SENSOR_PIN):
            lux = random.uniform(300, 1000)  # Simulate bright environment
        else:
            lux = random.uniform(0, 299)     # Simulate dark environment
    else:
        lux = random.uniform(0, 1000)        # Fully virtual
    return {"lux": lux}

def light_tracking():
    """Tracks and logs light sensor data continuously."""
    print("🔆 Light Sensor (Physical/Virtual) Active...")
    print("Press Ctrl+C to stop.")

    while True:
        light_data = get_light_level()
        log_light_data(light_data)
        send_data_to_cloud(light_data)
        send_data_to_azure(light_data)
        time.sleep(5)

if __name__ == "__main__":
    try:
        light_tracking()
    except KeyboardInterrupt:
        if REAL_SENSOR:
            GPIO.cleanup()
        print("\n🛑 Stopping light sensor tracking...")
