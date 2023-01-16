import asyncio
import websockets
import traceback
import serial
import pynmea2
import queue
import os

from json import dumps
from subprocess import Popen
from threading import Thread

last_point = "never read from GPS antenna yet"
points = queue.Queue()

def read_gps():
    global last_point, points
    port = "/dev/ttyAMA0"
    ser = serial.Serial(port, baudrate=9600, timeout=0.5)
    once = False
    while True:
        sentence = ser.readline()
        header = sentence[0:6]
        if header in (b"$GNRMC", b"$GPRMC", b"$GLRMC"):
            coordinates = pynmea2.parse(sentence.decode("utf-8"))
            point = {"lng": coordinates.longitude, "lat": coordinates.latitude}
            points.put(point)
            if not once:
                print(f"GPS says: {point} ({sentence})")
                once = True


def keep_running(cmd):
    while True:
        print(f"starting: {cmd}")
        with Popen(cmd, shell=True) as proc:
            print(f"started: {cmd}")
            ret = proc.wait()
            print(f"exit code {ret}: {cmd}")


def download_last_point():
    global last_point, points
    while True:
        try:
            last_point = points.get(False)
        except queue.Empty:
            return


async def handler(websocket, path):
    print(f"Client connected (path: {path})")

    # did this client want coordinates? send updates every 5 seconds
    if path.endswith("/coordinates"):
        global last_point
        while True:
            download_last_point()  # get the last point obtained from GPS
            if last_point is not None:
                await websocket.send(dumps(last_point))  # and send it to the client
            await asyncio.sleep(5)

    # or maybe this client wants to control the movement?
    if path.endswith("/control"):
        while True:
            request = await websocket.recv()
            reply = handle(request, websocket)
            await websocket.send(reply)



def handle(request, websocket):
    print(f"Received: {request}")
    if request == "reset-video":
        Popen("killall libcamera-vid", shell=True).wait() # todo: switch to asyncio.Popen
        return "stopped old video server"
    if request == "go-right":
        return "going right"
    if request == "go-left":
        return "going left"
    # otherwise, we are here
    return "unknown command: " + str(request)


def generate_static_pages():
    google_api_key = os.getenv("GOOGLE_API_KEY", "GOOGLE_API_KEY_NOT_FOUND")
    map_page = os.path.join(os.path.dirname(__file__), "html/map/index.html")
    print(f"Google API key: {google_api_key}")
    with open(map_page + ".template", "r") as template:
        with open(map_page, "w") as result:
            result.write(template.read().replace("YOUR_GOOGLE_API_KEY", google_api_key))
            print(f"Successfully created a static map page at {map_page}")


generate_static_pages()

videoserver = Thread(target=keep_running, args=("libcamera-vid -t 0 --width 640 --height 480 --codec h264 --inline --listen -o tcp://0.0.0.0:8000", ), daemon=True)
videoserver.start()

websockify = Thread(target=keep_running, args=("websockify 0.0.0.0:8001 0.0.0.0:8000", ), daemon=True)
websockify.start()

gpsreader = Thread(target=read_gps, args=(), daemon=True)
gpsreader.start()

webserver = websockets.serve(handler, "localhost", 8002)
asyncio.get_event_loop().run_until_complete(webserver)
asyncio.get_event_loop().run_forever()
