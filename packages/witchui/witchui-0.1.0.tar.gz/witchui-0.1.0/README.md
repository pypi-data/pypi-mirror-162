# Witchui

Helpful utilities for designing text-based interfaces on top of curses.


## Usage

See an example below, showing usage of some of the tools provided.


```python
import curses
from witchui import (
    setup_curses_colors,
    WindowPrinter,
    TitleText,
    SelectionDropdown,
    InputText,
)

def main(window):
    curses.curs_set(0)
    setup_curses_colors()

    window.clear()
    wprinter = WindowPrinter(window)
    wprinter.print(TitleText("My title"))
    wprinter.print("Choose from the list below:")

    possible_choices = ["apples", "bananas", "oranges"]
    selection = SelectionDropdown(window, possible_choices, line=2, col=4)
    selected_option = selection.run()

    input_text = InputText(window, line=6, col=2).run()

curses.wrapper(main)
```
