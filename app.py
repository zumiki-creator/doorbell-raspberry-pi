from gpiozero import LED, Button
from time import sleep
from arduino_iot_cloud import ArduinoCloudClient
import time
import logging
from signal import pause
import secrets




led1 = LED(14)
button1 = Button(2)

# This function is executed each time the "running" cloud variable changes
def on_switch_changed(client, value):
    print("Running: ", value)
    # led1.toggle()

def button1_pressed_action():
    print("Button was pressed!")
    client["cloud_send_notification"] = True
    led1.on()
    sleep(2)
    client["cloud_send_notification"] = False
    led1.off()



def logging_func():
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )


if __name__ == "__main__":
    DEVICE_ID = secrets.DEVICE_ID
    SECRET_KEY = secrets.SECRET_KEY

    print("start")
    button1.when_pressed = button1_pressed_action

    logging_func()
    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY)

    client.register("cloud_send_notification")

    client.register("running", value=None, on_write=on_switch_changed)
    client.start()
    print("client started")
    # Keep the script running to monitor for button presses
    pause()

