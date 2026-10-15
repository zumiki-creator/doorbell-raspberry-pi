import logging
import math
import threading
import time
from signal import pause
from time import sleep

try:
    from gpiozero import LED, Button
except ImportError:  # pragma: no cover - only used on non-Raspberry systems
    LED = None
    Button = None

try:
    from arduino_iot_cloud import ArduinoCloudClient
except ImportError:  # pragma: no cover - only used on systems without the package
    ArduinoCloudClient = None

try:
    from ultralytics import YOLO
except ImportError:  # pragma: no cover - only used when the package is unavailable
    YOLO = None

try:
    import cv2
except ImportError:  # pragma: no cover - only used when OpenCV is unavailable
    cv2 = None

import secrets


# object classes
classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]


# dection action functions

def check_thread_by_name(thread_name):
    """Checks if a thread with the given name is currently active."""
    for thread in threading.enumerate():
        if thread.name == thread_name:
            return True
    return False


def person_detected(client, x1, start_person_detected_mills):
    while True:
        current_time_millis = int(round(time.time() * 1000))
        elapsed_time_seconds = (current_time_millis - start_person_detected_mills) / 1000.0
        time.sleep(1)
        if elapsed_time_seconds >= x1:
            print("################################ ready for new person detection.")
            client["cloud_person_detected"] = False
            break


def laptop_detected():
    print("################################ ready for new laptop detection.")


def camera(cap, model, client, start_person_detected_mills):
    if cap is None or model is None or cv2 is None:
        return

    success, img = cap.read()
    if not success or img is None:
        return

    results = model(img, stream=True)

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            confidence = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])

            print("Class name -->", classNames[cls])
            if classNames[cls] == "person":
                print("PERSON DETECTED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                if not check_thread_by_name("PersonDetectionThread"):
                    client["cloud_person_detected"] = True
                    start_person_detected_mills[0] = int(round(time.time() * 1000))
                    person_thread = threading.Thread(
                        target=person_detected,
                        args=(client, 120, start_person_detected_mills[0]),
                        name="PersonDetectionThread",
                    )
                    person_thread.start()
                    print("Detection Person Reset")
                else:
                    start_person_detected_mills[0] = int(round(time.time() * 1000))

            if classNames[cls] == "laptop":
                print("LAPTOP DETECTED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                laptop_thread = threading.Thread(target=laptop_detected, name="LaptopDetectionThread")
                laptop_thread.start()
                print("Detection Laptop Reset")

            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2
            cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)


# This function is executed each time the "running" cloud variable changes
def on_switch_changed(client, value):
    print("Running: ", value)


# Button press action
def button1_pressed_action(client, led1):
    print("Button was pressed!")
    client["cloud_send_notification"] = True
    led1.on()
    sleep(2)
    client["cloud_send_notification"] = False
    led1.off()


# Logging function
def logging_func():
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )


def main():
    if LED is None or Button is None or ArduinoCloudClient is None or cv2 is None or YOLO is None:
        raise RuntimeError(
            "This app requires the Raspberry Pi and Python dependencies to be installed. "
            "See the project README and bootstrap script for setup instructions."
        )

    DEVICE_ID = secrets.DEVICE_ID
    SECRET_KEY = secrets.SECRET_KEY

    print("start")
    logging_func()
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY)

    led1 = LED(14)
    button1 = Button(2)

    def button_pressed_action():
        button1_pressed_action(client, led1)

    button1.when_pressed = button_pressed_action

    client.register("cloud_send_notification")
    client.register("cloud_person_detected")
    client["cloud_person_detected"] = False
    client.register("running", value=None, on_write=lambda client, value: on_switch_changed(client, value))

    start_person_detected_mills = [int(round(time.time() * 1000))]

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    model = YOLO("yolo-Weights/yolo11n.pt")

    def run_camera_loop():
        while True:
            camera(cap, model, client, start_person_detected_mills)
            time.sleep(0.1)

    camera_thread = threading.Thread(target=run_camera_loop, name="loop", daemon=True)
    camera_thread.start()

    print("client started")
    client.start()
    pause()

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

