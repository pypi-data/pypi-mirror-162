# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stonetech']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'stonetech',
    'version': '0.0.1',
    'description': 'Easter Egg to Codigo[S] - From Stone Tech',
    'long_description': None,
    'author': 'Enderson Menezes',
    'author_email': 'endersonster@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
