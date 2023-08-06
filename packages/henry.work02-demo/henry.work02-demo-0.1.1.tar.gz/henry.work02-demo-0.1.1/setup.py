# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['henry_work02_demo']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'henry.work02-demo',
    'version': '0.1.1',
    'description': '',
    'long_description': None,
    'author': 'Hyun Tae Kim',
    'author_email': 'henry.work02@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
