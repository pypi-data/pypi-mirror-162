import curses


def setup_curses_colors():
    curses.use_default_colors()
    colors = [
        curses.COLOR_BLACK,
        curses.COLOR_WHITE,
        curses.COLOR_RED,
        curses.COLOR_GREEN,
        curses.COLOR_BLUE,
        curses.COLOR_CYAN,
        curses.COLOR_MAGENTA,
        curses.COLOR_YELLOW,
    ]
    for pair_num, color in enumerate(colors):
        curses.init_pair(pair_num + 1, color, -1)
    return colors


class TextBit:
    def __init__(self, text, effects=0):
        self.text = text
        self.effects = effects
        self.line = None
        self.col = None

    def decorate(self, effect):
        self.effects ^= effect
        return self

    def bold(self):
        return self.decorate(curses.A_BOLD)

    def underlined(self):
        return self.decorate(curses.A_UNDERLINE)

    def centered(self):
        window_center = curses.COLS / 2
        self.col = int(window_center - len(self.text) / 2)
        return self

    def black(self):
        return self.decorate(curses.color_pair(1))

    def white(self):
        return self.decorate(curses.color_pair(2))

    def red(self):
        return self.decorate(curses.color_pair(3))

    def green(self):
        return self.decorate(curses.color_pair(4))

    def blue(self):
        return self.decorate(curses.color_pair(5))

    def cyan(self):
        return self.decorate(curses.color_pair(6))

    def magenta(self):
        return self.decorate(curses.color_pair(7))

    def yellow(self):
        return self.decorate(curses.color_pair(8))

    def indent(self, indent):
        self.col = indent


class TitleText(TextBit):
    def __init__(self, text, effects=0):
        super().__init__(text, effects)
        self.centered().underlined().bold()
