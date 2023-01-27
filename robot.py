import asyncio, pigpio, atexit
from subprocess import Popen


# our motors are connected to pins 19 and 18
left_motor_pin = 18
right_motor_pin = 19


# the classic RC protocol (yes, I know it is very simple, just saying it how it is)
FULL_FORWARD = 2000
FULL_REVERSE = 1000
STOP = 1500

# connect!
pi = pigpio.pi()
pi.set_servo_pulsewidth(left_motor_pin, STOP)
pi.set_servo_pulsewidth(right_motor_pin, STOP)


async def handle_command(command):
    global pi, right_motor_pin, left_motor_pin

    if command == "go-right":
        # start spinning left motor
        pi.set_servo_pulsewidth(left_motor_pin, FULL_REVERSE)
        # wait 0.50 seconds
        await asyncio.sleep(0.5)
        # stop spinning left motor
        pi.set_servo_pulsewidth(left_motor_pin, STOP)
        return "robot went of the bridge"
    
    if command == "go-forward":
        # start spinning right motor
        pi.set_servo_pulsewidth(right_motor_pin, FULL_REVERSE)
        pi.set_servo_pulsewidth(left_motor_pin, FULL_REVERSE)
        # wait 0.50 seconds
        await asyncio.sleep(2)
        # stop spinning right motor
        pi.set_servo_pulsewidth(right_motor_pin, STOP)
        pi.set_servo_pulsewidth(left_motor_pin, STOP)
        return "robot went forward"

    if command == "go-left":
        # start spinning right motor
        pi.set_servo_pulsewidth(right_motor_pin, FULL_REVERSE)
        # wait 0.50 seconds
        await asyncio.sleep(0.5)
        # stop spinning right motor
        pi.set_servo_pulsewidth(right_motor_pin, STOP)
        return "robot went kaboom"

    if command == "reset-video":
        Popen("killall libcamera-vid", shell=True).wait() # todo: switch to asyncio.Popen
        return "stopped old video server"

    # otherwise, we are here
    return "unknown command: " + str(command)


# how to stop in the case of exit
def _stop():
    global pi, right_motor_pin, left_motor_pin
    print("Stopping pigpio connection")
    # 0 means "shutdown" here (in the case of drones/planes it means "failsafe": for example, return home and land)
    pi.set_servo_pulsewidth(right_motor_pin, 0)
    pi.set_servo_pulsewidth(left_motor_pin, 0)
    pi.stop()
    print("Stopped pigpio connection")


atexit.register(_stop)
