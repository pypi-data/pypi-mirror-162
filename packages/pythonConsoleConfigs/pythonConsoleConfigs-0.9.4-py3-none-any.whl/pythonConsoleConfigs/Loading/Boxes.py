from pythonConsoleConfigs.Font import Color as c
from pythonConsoleConfigs.Loading.helper import run


class Box:
    def __init__(self, duration, size, color=c.WHITE, reverse=False):
        self.seconds = duration
        self.color = color
        self.reverse = reverse
        self.__emptyBox__ = "□"
        self.__fullBox__ = "■"
        self.__rate__(size)

    def __rate__(self, size):
        animation = []
        accumulator = size - 1
        if self.reverse:
            self.__emptyBox__, self.__fullBox__ = self.__fullBox__, self.__emptyBox__

        for r in range(1, size + 1):
            animation.append(self.__fullBox__ * r + self.__emptyBox__ * accumulator)
            accumulator -= 1
        self.animation = animation

    def loading(self):
        run(self.color, self.animation, self.seconds)
