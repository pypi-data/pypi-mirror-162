# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sneakpeak']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sneakpeak',
    'version': '0.1.1',
    'description': 'A python module to generate data for link preview.',
    'long_description': '',
    'author': 'Ameya Shenoy',
    'author_email': 'shenoy.ameya@gmail.com',
    'maintainer': 'Ameya Shenoy',
    'maintainer_email': 'shenoy.ameya@gmail.com',
    'url': 'https://github.com/codingcoffee/sneakpeak',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
