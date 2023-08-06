# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['clock_cli']

package_data = \
{'': ['*']}

install_requires = \
['arrow>=1.2.2,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'tabulate>=0.8.10,<0.9.0',
 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['clock = clock:cli']}

setup_kwargs = {
    'name': 'clock-cli',
    'version': '0.1.0',
    'description': 'A command-line time zone converter',
    'long_description': None,
    'author': 'Chris Proctor',
    'author_email': 'github.com@accounts.chrisproctor.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
