# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['privy_python_sdk']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'privy-python-sdk',
    'version': '1.0.0',
    'description': 'Python SDK for Privy Digital Signature',
    'long_description': None,
    'author': 'LandX',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
