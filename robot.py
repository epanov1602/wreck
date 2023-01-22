import asyncio, pigpio, atexit
from subprocess import Popen


left_motor_pin = 19
right_motor_pin = 18
pi = pigpio.pi()


async def handle_command(command):
    global pi, right_motor_pin, left_motor_pin

    if command == "go-right":
        # start spinning left motor
        pi.set_servo_pulsewidth(left_motor_pin, 2000)
        # wait 2 seconds
        await asyncio.sleep(2)
        # stop spinning left motor
        pi.set_servo_pulsewidth(left_motor_pin, 0)
        return "robot went right"

    if command == "go-left":
        # start spinning right motor
        pi.set_servo_pulsewidth(right_motor_pin, 2000)
        # wait 2 seconds
        await asyncio.sleep(2)
        # stop spinning right motor
        pi.set_servo_pulsewidth(right_motor_pin, 0)
        return "robot went left"

    if command == "reset-video":
        Popen("killall libcamera-vid", shell=True).wait() # todo: switch to asyncio.Popen
        return "stopped old video server"

    # otherwise, we are here
    return "unknown command: " + str(command)


# how to stop in the case of exit
def _stop():
    global pi, right_motor_pin, left_motor_pin
    print("Stopping pigpio connection")
    pi.set_servo_pulsewidth(right_motor_pin, 0)
    pi.set_servo_pulsewidth(left_motor_pin, 0)
    pi.stop()
    print("Stopped pigpio connection")

atexit.register(_stop)
