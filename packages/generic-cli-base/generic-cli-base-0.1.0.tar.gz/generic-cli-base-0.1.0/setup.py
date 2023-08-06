# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['generic_cli_base']

package_data = \
{'': ['*']}

install_requires = \
['Cerberus>=1.3.4,<2.0.0', 'PyYAML>=6.0,<7.0', 'click>=8.1.3,<9.0.0']

setup_kwargs = {
    'name': 'generic-cli-base',
    'version': '0.1.0',
    'description': 'A simple Commandline Application Base',
    'long_description': None,
    'author': 'Mark Hall',
    'author_email': 'mark.hall@work.room3b.eu',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
