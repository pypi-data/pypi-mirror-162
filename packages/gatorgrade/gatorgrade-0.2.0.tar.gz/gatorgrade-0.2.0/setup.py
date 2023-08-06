# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gatorgrade', 'gatorgrade.generate', 'gatorgrade.input', 'gatorgrade.output']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'gatorgrader>=1.1.0,<2.0.0',
 'rich>=12.5.1,<13.0.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['gatorgrade = gatorgrade.main:app']}

setup_kwargs = {
    'name': 'gatorgrade',
    'version': '0.2.0',
    'description': 'Python tool to execute GatorGrader',
    'long_description': None,
    'author': 'Michael Abraham',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
