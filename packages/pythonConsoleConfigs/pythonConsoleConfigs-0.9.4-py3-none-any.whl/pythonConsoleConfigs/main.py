from Font import Color, Style, Highlight
from Loading import Box, Percentage


def printTesting(msg, color, reset=True):
    print(f'{color}{msg}')
    if reset:
        Style().reset()


if __name__ == '__main__':
    printTesting('This is a test of Python Console Configuration Library', Color.MAGENTA)
    printTesting('This is a test of Python Console Configuration Library', Style.BLINK)
    printTesting('This is a test of Python Console Configuration Library', Highlight.BLUE)
    printTesting('This is a test of Python Console Configuration Library', Color.CYAN)
    printTesting('This is a test of Python Console Configuration Library', Color.LIGHT_CYAN)
    printTesting('This is a test of Python Console Configuration Library', Color.LIGHT_RED)
    print("TEST OF RESET")

    Box(duration=1, size=15, color=Color.BLUE, reverse=True).loading()
    Percentage(duration=1, rate=10, color=Color.RED).loading()
