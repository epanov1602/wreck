import asyncio
import websockets
import traceback
import serial
import pynmea2
import queue

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


videoserver = Thread(target=keep_running, args=("libcamera-vid -t 0 --width 640 --height 480 --codec h264 --inline --listen -o tcp://0.0.0.0:8000", ))
videoserver.start()

websockify = Thread(target=keep_running, args=("websockify 0.0.0.0:8001 0.0.0.0:8000", ))
websockify.start()

gpsreader = Thread(target=read_gps, args=())
gpsreader.start()


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
            msg = await websocket.recv()
            print(f"Received: {msg}")
            reply = respond(msg, websocket)
            await websocket.send(reply)



def respond(msg, websocket):
    if msg == "reset-video":
        Popen("killall libcamera-vid", shell=True).wait() # todo: switch to asyncio.Popen
        return "stopped old video server"
    if msg == "go-right":
        return "going right"
    if msg == "go-left":
        return "going left"
    # otherwise, we are here
    return "unknown command: " + str(msg)


start_server = websockets.serve(handler, "localhost", 8002)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()