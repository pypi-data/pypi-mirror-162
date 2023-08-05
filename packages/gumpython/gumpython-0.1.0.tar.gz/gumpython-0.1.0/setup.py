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
    'version': '0.1.0',
    'description': 'A python library for gum cli',
    'long_description': None,
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
