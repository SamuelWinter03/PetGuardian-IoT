import time
import json
import os
import cv2  # OpenCV for image capture
import paho.mqtt.client as mqtt

# MQTT settings
BROKER = "broker.hivemq.com"
TOPIC = "petguardian/iot"
SAVE_DIR = "captured_images"

# Ensure the save directory exists
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def send_data_to_cloud(image_path):
    """Send camera event metadata to MQTT broker and delete image after sending."""
    client = mqtt.Client()
    client.connect(BROKER)
    client.loop_start()  # Start network loop in background

    payload = json.dumps({
        "sensor": "camera",
        "image_path": image_path,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    print(f"📤 Publishing to {BROKER} on topic '{TOPIC}'")
    client.publish(TOPIC, str(payload), retain=True)  # Wrap in str() for HiveMQ display
    time.sleep(3)  # Give time for message to go through
    client.loop_stop()
    client.disconnect()

    print(f"✅ Sent Camera Data to MQTT Broker: {payload}")

    # Delete the image after sending
    try:
        os.remove(image_path)
        print(f"🗑️ Deleted Image: {image_path}")
    except Exception as e:
        print(f"❌ Error deleting image: {e}")

def capture_image():
    """Captures an image using the USB webcam."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    image_path = os.path.join(SAVE_DIR, f"image_{timestamp}.jpg")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("🚫 Could not open webcam.")
        return

    ret, frame = cap.read()
    cap.release()

    if ret:
        cv2.imwrite(image_path, frame)
        print(f"📸 Image Captured: {image_path}")
        send_data_to_cloud(image_path)
    else:
        print("⚠️ Failed to capture image.")

def camera_trigger():
    """Manual test trigger loop (press ENTER to capture, 'x' to exit)."""
    print("\n📷 Camera Sensor Active...\nPress ENTER to capture an image, type 'x' to exit.\n")

    while True:
        cmd = input("? Enter command: ").strip().lower()
        if cmd == "x":
            print("👋 Stopping camera sensor...")
            break
        else:
            capture_image()

if __name__ == "__main__":
    try:
        camera_trigger()
    except KeyboardInterrupt:
        print("\n🛑 Exiting camera sensor...")
