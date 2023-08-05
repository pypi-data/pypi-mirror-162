# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['touchboard']

package_data = \
{'': ['*']}

install_requires = \
['pyautogui>=0.9.53', 'python3-xlib>=0.15']

setup_kwargs = {
    'name': 'touchboard',
    'version': '0.1.3',
    'description': '',
    'long_description': "# Installation:\n\nRun ```pip install touchboard ==0.1.0```. Replace the version (0.1.0) with your corresponding version by operating system (0.1.0 for windows, 0.1.3 for linux, or 0.1.2 for macos)\n\n#### Note: This has ONLY been tested on windows.\n# Code:\n\n```py\nimport touchboard\n\ntouchboard.begin('SERIAL PORT HERE')\n```\n",
    'author': 'Python Nerd',
    'author_email': 'prajwalmisc@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
