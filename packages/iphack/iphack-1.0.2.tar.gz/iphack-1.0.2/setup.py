# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['iphack']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'iphack',
    'version': '1.0.2',
    'description': 'the most ideal tool for finding out information about IP: github.com/mishakorzik/IpHack',
    'long_description': None,
    'author': 'MishaKorzhik_He1Zen',
    'author_email': 'miguardzecurity@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
