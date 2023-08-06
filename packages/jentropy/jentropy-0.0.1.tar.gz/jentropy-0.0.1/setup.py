# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jentropy']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'jentropy',
    'version': '0.0.1',
    'description': 'placeholder',
    'long_description': None,
    'author': 'Jader Brasil',
    'author_email': 'jaderbrasil@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
