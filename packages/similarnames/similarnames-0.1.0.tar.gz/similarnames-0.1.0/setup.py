# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['similarnames']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'similarnames',
    'version': '0.1.0',
    'description': 'Library for Standardizing names from a Pandas dataframe',
    'long_description': None,
    'author': 'paulobrunheroto',
    'author_email': 'paulobrunheroto@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
