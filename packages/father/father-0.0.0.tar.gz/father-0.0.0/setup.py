# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['father']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'father',
    'version': '0.0.0',
    'description': '',
    'long_description': None,
    'author': 'githashem',
    'author_email': 'PersonalHashem@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
