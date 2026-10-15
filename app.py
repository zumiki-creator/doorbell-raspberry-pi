# arduino iot cloud
from gpiozero import LED, Button
from time import sleep
from arduino_iot_cloud import ArduinoCloudClient
import time
import logging
from signal import pause
import secrets

led1 = LED(14)
button1 = Button(2)
# end arduino iot cloud

from ultralytics import YOLO
import cv2
import math
import sys

import threading
import time

# dection action functions

def check_thread_by_name(thread_name):
    """Checks if a thread with the given name is currently active."""
    for thread in threading.enumerate():
        if thread.name == thread_name:
            return True
    return False

def person_detected(x1, start_person_detected_mills):
    while True:
        current_time_millis = int(round(time.time() * 1000))
        elapsed_time_seconds = (current_time_millis - start_person_detected_mills) / 1000.0
        time.sleep(1)
        # print(f"##################### start_person_detected_mills: {start_person_detected_mills}")
        # print(f"##################### current_time_millis: {current_time_millis}")
        # print(f"##################### elapsed_time_seconds: {elapsed_time_seconds}")
        if elapsed_time_seconds >= x1:
            print("################################ ready for new person detection.")
            client["cloud_person_detected"] = False
            break

def laptop_detected():
    # client["cloud_laptop_detected"] = False
    print("################################ ready for new laptop detection.")

def camera():
    success, img = cap.read()
    results = model(img, stream=True)

    for thread in threading.enumerate():
        print(f"  - {thread.name} (Daemon: {thread.daemon}, Alive: {thread.is_alive()})")

    # coordinates
    for r in results:
        boxes = r.boxes

        for box in boxes:
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

            # put box in cam
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # confidence
            confidence = math.ceil((box.conf[0]*100))/100
            # print("Confidence --->",confidence)

            # class name
            cls = int(box.cls[0])

            print("Class name -->", classNames[cls])
            global start_person_detected_mills
            if classNames[cls] == "person":
                print("PERSON DETECTED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                
                if not check_thread_by_name("PersonDetectionThread"):
                    client["cloud_person_detected"] = True 
                    start_person_detected_mills = int(round(time.time() * 1000))
                    person_thread = threading.Thread(target=person_detected, args=(120, start_person_detected_mills), name="PersonDetectionThread") 
                    person_thread.start()                
                    print("Detection Person Reset")
                else:
                    start_person_detected_mills = int(round(time.time() * 1000))

            if classNames[cls] == "laptop":
                print("LAPTOP DETECTED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                laptop_thread = threading.Thread(target=laptop_detected, name="LaptopDetectionThread") 
                laptop_thread.start()
                print("Detection Laptop Reset")

            # object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2
            cv2.putText(img, classNames[cls], org, font, fontScale, color, thickness)

    # cv2.imshow('Webcam', img)
    # if cv2.waitKey(1) == ord('q'):
    #    break
    threading.Thread(target=camera, name="loop").start()

# This function is executed each time the "running" cloud variable changes
def on_switch_changed(client, value):
    print("Running: ", value)
    # led1.toggle()

# Button press action
def button1_pressed_action():
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

############################# MAIN CODE #############################

DEVICE_ID = secrets.DEVICE_ID
SECRET_KEY = secrets.SECRET_KEY

print("start")
button1.when_pressed = button1_pressed_action

logging_func()
client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY)

client.register("cloud_send_notification")

client.register("cloud_person_detected")
client["cloud_person_detected"] = False

client.register("running", value=None, on_write=on_switch_changed)

start_person_detected_mills = int(round(time.time() * 1000))

# start webcam
cap = cv2.VideoCapture(0) # on PC (0) for builtin webcam / (4) for usb webcam. on raspberry pi use (0) for the pi camera and webcam
cap.set(3, 640)
cap.set(4, 480)

# model
model = YOLO("yolo-Weights/yolo11n.pt")

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


camera()

print("client started")
client.start()   

cap.release()
cv2.destroyAllWindows()
