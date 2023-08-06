from pythonConsoleConfigs.Font import Color as c
from pythonConsoleConfigs.Loading.helper import run


class Percentage:
    def __init__(self, duration, rate, color=c.WHITE):
        self.seconds = duration
        self.color = color
        self.__rate__(rate)

    def __rate__(self, rate):
        if 100 % rate == 0:
            animation = []
            for r in range(1, int(100 / rate) + 1):
                animation.append((str(r * rate) + "%"))
            self.animation = animation

    def loading(self):
        try:
            run(self.color, self.animation, self.seconds)
        except AttributeError:
            raise Exception("Error, rate must be divisor of 100!")
