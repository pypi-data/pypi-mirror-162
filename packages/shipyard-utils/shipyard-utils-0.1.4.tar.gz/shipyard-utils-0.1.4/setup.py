# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['shipyard_utils']

package_data = \
{'': ['*'], 'shipyard_utils': ['blake-artifacts/vvv-blueprints/variables/*']}

install_requires = \
['python-dateutil==2.8.2']

setup_kwargs = {
    'name': 'shipyard-utils',
    'version': '0.1.4',
    'description': 'Small scripts and utilities to make Shipyard Blueprint development easier.',
    'long_description': None,
    'author': 'Blake Burch',
    'author_email': 'blake@shipyardapp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
