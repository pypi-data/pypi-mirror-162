import curses

from .printer import WindowPrinter


class InputText:
    def __init__(self, window, line=0, col=0, input_symbol=">"):
        self.window = window
        self.printer = WindowPrinter(window)
        self.line = line
        self.col = col
        self.symbol = input_symbol
        self.text = ""

    def on_keypress(self, char_pressed):
        if char_pressed == 10:  # Enter key
            return True

    def draw(self):
        self.printer.line = self.line
        self.printer.col = self.col
        self.printer.print(f"{self.symbol} ", indent=self.col)
        self.window.move(self.line, self.col)

    def run(self):
        self.window.move(self.line, self.col)
        curses.curs_set(1)
        curses.echo()

        self.draw()
        self.text = self.window.getstr(self.line, self.col + 2).decode("utf-8")

        curses.curs_set(0)
        return self.text
