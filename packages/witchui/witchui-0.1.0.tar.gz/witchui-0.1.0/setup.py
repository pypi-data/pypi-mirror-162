# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['witchui']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'witchui',
    'version': '0.1.0',
    'description': 'Helpful tools for designing text-based interfaces, based on curses.',
    'long_description': '# Witchui\n\nHelpful utilities for designing text-based interfaces on top of curses.\n\n\n## Usage\n\nSee an example below, showing usage of some of the tools provided.\n\n\n```python\nimport curses\nfrom witchui import (\n    setup_curses_colors,\n    WindowPrinter,\n    TitleText,\n    SelectionDropdown,\n    InputText,\n)\n\ndef main(window):\n    curses.curs_set(0)\n    setup_curses_colors()\n\n    window.clear()\n    wprinter = WindowPrinter(window)\n    wprinter.print(TitleText("My title"))\n    wprinter.print("Choose from the list below:")\n\n    possible_choices = ["apples", "bananas", "oranges"]\n    selection = SelectionDropdown(window, possible_choices, line=2, col=4)\n    selected_option = selection.run()\n\n    input_text = InputText(window, line=6, col=2).run()\n\ncurses.wrapper(main)\n```\n',
    'author': 'Ana Filipe',
    'author_email': 'ana.filipe@miniclip.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
