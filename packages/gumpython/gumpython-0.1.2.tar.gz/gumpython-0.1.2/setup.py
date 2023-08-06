# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gumpython',
 'gumpython.arguments',
 'gumpython.commands',
 'gumpython.flags',
 'gumpython.inputs',
 'gumpython.inputs.help_inputs']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'gumpython',
    'version': '0.1.2',
    'description': 'A python library for gum cli',
    'long_description': '# GumPython\n A python library for gum cli\n\n## Requirements\n\n- [gum cli](https://github.com/charmbracelet/gum)\n- Python >= 3.8\n\n## How to Use\n\n```python\nfrom gumpython import Style, color, alignment, border\n\nstyle = Style(["Hi there!", "My name is GumPython :)"]) \\\n            .border(border.ROUNDED, foreground_color=color.FUCHSIA) \\\n            .text_color(foreground=color.AQUA) \\\n            .align(alignment=alignment.CENTER) \\\n            .text_font(bold=True, italic=True)\n\nstyle.run()\n```',
    'author': 'Wasi Haider',
    'author_email': 'wsi.haidr@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
