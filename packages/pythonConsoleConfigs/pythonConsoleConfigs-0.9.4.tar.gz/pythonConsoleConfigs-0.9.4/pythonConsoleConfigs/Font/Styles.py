class Style:
    BOLD = '\33[1m'
    ITALIC = '\33[3m'
    URL = '\33[4m'
    BLINK = '\33[5m'
    BLINK2 = '\33[6m'
    SELECTED = '\33[7m'
    __RESET = '\33[0m'

    def reset(self):
        print(self.__RESET, end="")
