from subprocess import Popen


def handle_command(request):
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

