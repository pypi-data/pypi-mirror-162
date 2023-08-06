# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nornir_nautobot',
 'nornir_nautobot.plugins',
 'nornir_nautobot.plugins.inventory',
 'nornir_nautobot.plugins.processors',
 'nornir_nautobot.plugins.tasks.dispatcher',
 'nornir_nautobot.utils']

package_data = \
{'': ['*']}

install_requires = \
['netutils>=1,<2',
 'nornir-jinja2>=0,<1',
 'nornir-napalm>=0,<1',
 'nornir-netmiko>=0,<1',
 'nornir-utils>=0,<1',
 'nornir>=3.0.0,<4.0.0',
 'pynautobot>=1.0.1,<2.0.0',
 'requests>=2.25.1,<3.0.0']

entry_points = \
{'nornir.plugins.inventory': ['NautobotInventory = '
                              'nornir_nautobot.plugins.inventory.nautobot:NautobotInventory']}

setup_kwargs = {
    'name': 'nornir-nautobot',
    'version': '2.2.2',
    'description': 'Nornir Nautobot',
    'long_description': "# nornir_nautobot\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n\n## Build Status\n\n| Branch  | Status                                                                                                                               |\n| ------- | ------------------------------------------------------------------------------------------------------------------------------------ |\n| develop | [![CI](https://github.com/nautobot/nornir-nautobot/actions/workflows/ci.yml/badge.svg)](https://github.com/nautobot/nornir-nautobot/actions/workflows/ci.yml) |\n## Overview\n\nThe nornir_nautobot project intends to solve two primary use cases.\n\n* Providing a Nornir inventory that leverages Nautobot's API.\n* A set of opinionated Nornir plugins.\n\nThe set of plugins intend to provide mechanisms to include common networking workflows that will help enable network automation. As an example, there are method to get configurations or test network connectivity. Over time this will include functions to perform actions such as get vlans, neighbors, protocols, etc.\n\n## Getting Started\n\n```shell\npip install nornir-nautobot\n```\n\n## Documentation Link\n\nThe documentation can be found on [Read the Docs](https://nornir-nautobot.readthedocs.io/en/latest/)\n\n## Nautobot\n\nNautobot documentation is available at [Nautobot Read the Docs](https://nautobot.readthedocs.io/en/latest/)\n",
    'author': 'Network to Code, LLC',
    'author_email': 'opensource@networktocode.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://nautobot.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
