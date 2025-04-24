import threading
import time
import logging
from sensors import gps_sensor, camera_sensor, acoustic_sensor
from ai import ai_controller

logging.getLogger("azure").setLevel(logging.ERROR)

def safe_start(name, func, stop_event):
    try:
        print(f" Starting {name} listener thread...")
        func(stop_event)
    except Exception as e:
        print(f"{name} thread crashed: {e}")

def run_acoustic_full(stop_event):
    acoustic_sensor.start_acoustic_listener()
    acoustic_sensor.start_acoustic_sensor(stop_event)

def main():
    stop_event = threading.Event()

    gps_thread = threading.Thread(target=safe_start, args=("GPS", gps_sensor.start_gps_listener, stop_event))
    cam_thread = threading.Thread(target=safe_start, args=("Camera", camera_sensor.start_camera_listener, stop_event))
    ai_thread = threading.Thread(target=safe_start, args=("AI", ai_controller.start_ai_listener, stop_event))
    acoustic_thread = threading.Thread(target=run_acoustic_full, args=(stop_event,))

    gps_thread.start()
    time.sleep(2)
    cam_thread.start()
    time.sleep(2)
    ai_thread.start()
    time.sleep(7)
    acoustic_thread.start()

    try:
        gps_thread.join()
        cam_thread.join()
        ai_thread.join()
        acoustic_thread.join()
    except KeyboardInterrupt:
        print("\n[EXIT] Ctrl+C detected. Stopping all threads...")
        stop_event.set()

if __name__ == "__main__":
    main()
