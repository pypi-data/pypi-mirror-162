import curses

from .text import TextBit


class WindowPrinter:
    def __init__(self, window):
        self.window = window
        self.line = 0
        self.col = 0

    def print(self, text, effects=0, indent=0):
        if not isinstance(text, TextBit):
            text = TextBit(text, effects)

        desired_col = text.col
        col = 0 if desired_col is None else desired_col
        col += indent
        self.window.move(self.line, 0)
        self.window.clrtoeol()
        self.window.addstr(self.line, col, text.text, text.effects)
        self.line += 1
        self.col = 0
        # self.window.move(self.line, self.col)

    def reset(self):
        self.window.clear()
        self.line = 0
        self.col = 0


class DebugPrinter:
    def __init__(self, window, line=-1):
        self.window = window
        self.line = line if line > -1 else curses.LINES - 1

    def print(self, text):
        if not isinstance(text, TextBit):
            text = TextBit(text).red()

        self.window.move(self.line, 0)
        self.window.clrtoeol()
        self.window.addstr(self.line, 0, text.text, text.effects)
