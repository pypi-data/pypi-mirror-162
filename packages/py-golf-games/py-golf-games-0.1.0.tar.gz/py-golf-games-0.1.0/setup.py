# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['py_golf_games', 'py_golf_games.games', 'py_golf_games.simulation']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'py-golf-games',
    'version': '0.1.0',
    'description': 'Simulation of golf games',
    'long_description': None,
    'author': 'Ryan',
    'author_email': 'ryankanno@localkinegrinds.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
