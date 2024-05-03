#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT-0

import RPi.GPIO as GPIO
import time
import json
from datetime import datetime
import cv2
import picamera2
import stream_manager
import awsiot.greengrasscoreipc.client as client
import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    SubscribeToIoTCoreRequest,
    QOS,
    IoTCoreMessage
)
from stream_manager.util import Util
import sys
import os

import RGB1602
import math
colorR = 64
colorG = 128
colorB = 64

# Initialize GPIO
GPIO.setmode(GPIO.BCM)  # Use BCM numbering scheme
GPIO.setwarnings(False)  # Disable warnings

# Pin configuration
button_pin = 18

# Set up the button pin as an input pin
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

cameraType = sys.argv[1]
buttonDebounce = int(sys.argv[2])
button_pin = int(sys.argv[3])

print(
    f"configuration ==> cameraType:{cameraType}-buttonDebounce:{buttonDebounce}-button_pin:{button_pin}")


LOCAL_RESOURCE_DIR = "/tmp"
cloud_bucket_name = os.getenv("TRASH_BUCKET")
thing_name = os.getenv("AWS_IOT_THING_NAME")
subscribe_topic = "$aws/things/"+thing_name+"/shadow/update/accepted"
# publish_topic = "smart/trash_bin"
sub_qos = QOS.AT_MOST_ONCE
pub_qos = QOS.AT_LEAST_ONCE
ipc_client = awsiot.greengrasscoreipc.connect()

# timestamp = datetime.now()
# lastUploaded = timestamp


def subscribeToShadowTopicForIntructions():
    # subscribe to shadow update topic
    try:
        print("Subscribing to MQTT topic for shadow")
        request = SubscribeToIoTCoreRequest()
        request.topic_name = subscribe_topic
        request.qos = sub_qos
        handler = StreamHandler()
        operation = ipc_client.new_subscribe_to_iot_core(handler)
        future = operation.activate(request)
        future.result(10)
    except Exception as ex:
        print("subscribeToShadowTopicForIntructions - Error", ex)
        raise


class StreamHandler(client.SubscribeToIoTCoreStreamHandler):
    def __init__(self):
        super().__init__()

    def on_stream_event(self, event: IoTCoreMessage) -> None:
        try:
            message_string = str(event.message.payload, "utf-8")
            # Load message and check values
            json_payload = json.loads(message_string)

            print("json_payload from cloud ##########:", json_payload)

            if json_payload['state']['desired']:
                if "classification" in json_payload['state']['desired']:
                    print("Display:",
                          json_payload['state']['desired']['classification'])
                    display(json_payload['state']['desired']['classification'])

        except Exception as ex:
            print(ex)
            raise
            # traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        # Handle error.
        return True  # Return True to close stream, False to keep stream open.

    def on_stream_closed(self) -> None:
        # Handle close.
        pass


def getCameraHandle(cameraType):
    # vs = None
    if cameraType == "picam":
        print("get picam handle")
        camera = picamera2.Picamera2()
        camera.preview_configuration.main.size = (1280, 720)
        camera.preview_configuration.main.format = "RGB888"
        camera.preview_configuration.align()
        camera.configure("preview")
        camera.start()
    elif cameraType == "webcam":
        camera = cv2.VideoCapture(0)
    return camera


class ImageStream():
    """Uploads images to S3 via the Greengrass Stream Mamanger"""

    def __init__(self):

        try:
            self.client = stream_manager.StreamManagerClient()
            self.stream_name = "waste-images"
            self.bucket = cloud_bucket_name

            if not self.stream_name in self.client.list_streams():
                options = stream_manager.MessageStreamDefinition(
                    name=self.stream_name,
                    strategy_on_full=stream_manager.StrategyOnFull.OverwriteOldestData,
                    export_definition=stream_manager.ExportDefinition(
                        s3_task_executor=[
                            stream_manager.S3ExportTaskExecutorConfig(
                                identifier=f"s3{self.stream_name}"
                            )
                        ]
                    ),
                )
                self.client.create_message_stream(options)
                print(f"Created new message stream {self.stream_name}")
            else:
                print(f"Using existing message stream {self.stream_name}")
        except Exception as ex:
            print("StreamManagerClient------#####-----", ex)
            raise

    def upload(self, destination_path: str, local_path: str) -> None:
        try:
            export_task = stream_manager.S3ExportTaskDefinition(
                input_url=f"file://{local_path}", bucket=cloud_bucket_name, key=destination_path
            )

            data = Util.validate_and_serialize_to_json_bytes(export_task)
            self.client.append_message(self.stream_name, data)
            print(f"Image uploaded to bucket {destination_path}")
        except Exception as ex:
            print(ex)
            raise


def create_image_filename():
    now = datetime.now()
    filename = "{}/{}-{}-{}-{}.jpg".format(LOCAL_RESOURCE_DIR,
                                           now.year, now.month, now.day,
                                           "raw")
    # current_time_millis = int(time.time() * 1000)
    # filename = LOCAL_RESOURCE_DIR + "/" + str(current_time_millis) + ".jpg"
    return filename


def readVideoStream(camerahandle):
    if cameraType == "webcam":
        ret, frame = camerahandle.read()
    else:
        frame = camerahandle.capture_array()

    return frame


def display(result):
    lcd = RGB1602.RGB1602(16, 2)
    rgb1 = (148, 0, 110)
    rgb2 = (255, 0, 255)
    rgb3 = (144, 249, 15)
    rgb4 = (0, 128, 60)
    rgb5 = (255, 209, 0)
    rgb6 = (248, 248, 60)
    rgb7 = (80, 80, 145)
    rgb8 = (255, 0, 0)
    rgb9 = (0, 255, 0)
    # set the cursor to column 0, line 1
    lcd.setCursor(0, 0)
    lcd.printout("AWS-LHR14")
    lcd.setCursor(0, 1)
    lcd.printout(result)
    # time.sleep(5)  # uncomment this line to wait 5 seconds before clearing the screen
    lcd.setCursor(0, 0)
    lcd.printout("AWS-LHR14")
    lcd.setCursor(0, 1)
    lcd.printout("Always Day1")


# def push_to_s3(filename, folder, classify):
def push_to_s3(filename):
    now = datetime.now()
    # key = str(folder) + "/{}-{}-{}-{}.jpg".format(
    #     now.year, now.month, now.day,
    #     classify)
    key = "public/{}-{}-{}-{}.jpg".format(
        now.year, now.month, now.day,
        "raw")

    Succeeded = False
    attempts = 4
    while not Succeeded and attempts > 0:
        try:
            uploader.upload(key, filename)
            Succeeded = True
        except stream_manager.StreamManagerException:
            attempts -= 1
            # time.sleep(2) # uncomment this line to wait 2 seconds before retrying
        except ConnectionError or TimeoutError:
            attempts -= 1
            # time.sleep(2) # uncomment this line to wait 2 seconds before retrying


def video_capture(filename, camera) -> None:
    for i in range(10):
        first_frame = readVideoStream(camera)
    first_frame = cv2.resize(first_frame, (600, 500))
    cv2.imwrite(filename, first_frame)
    return


def button_callback(channel):
    camera = getCameraHandle(cameraType)
    filename = create_image_filename()
    video_capture(filename, camera)
    push_to_s3(filename)
    # os.remove(filename)
    camera.release()


# Listen for instructions from cloud
subscribeToShadowTopicForIntructions()

try:
    uploader = ImageStream()
    # camera = getCameraHandle(cameraType)
    # if camera is not None:
    # Register the button press event
    GPIO.add_event_detect(button_pin, GPIO.FALLING,
                          callback=button_callback, bouncetime=buttonDebounce)
    print("Waiting for button press. Press Ctrl+C to exit.")
    while True:
        time.sleep(1)  # Keep the program running

except KeyboardInterrupt:
    print("Exiting program.")
except Exception as ex:
    print("ImageStream class ------#####-----", ex)
    raise

finally:
    GPIO.cleanup()  # Clean up GPIO settings
