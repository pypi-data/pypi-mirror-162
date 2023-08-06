import sys
import time

from pythonConsoleConfigs.Font import Style as s


def run(color, animation, duration):
    print(color, end="")
    for i in range(len(animation)):
        time.sleep(duration)
        sys.stdout.write("\r" + animation[i % len(animation)])
        sys.stdout.flush()
    s().reset()
