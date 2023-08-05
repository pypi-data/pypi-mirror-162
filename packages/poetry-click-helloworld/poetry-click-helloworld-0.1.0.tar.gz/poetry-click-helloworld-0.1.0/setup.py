# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['poetry_click_helloworld']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0']

entry_points = \
{'console_scripts': ['pchw = poetry_click_helloworld.main:main']}

setup_kwargs = {
    'name': 'poetry-click-helloworld',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Michael Ramos',
    'author_email': 'michaeltramos@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
