# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['infra_copilot']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'infra-copilot',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Eduardo Guadanhim',
    'author_email': 'eduardo.guadanhim@synchro.com.br',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
