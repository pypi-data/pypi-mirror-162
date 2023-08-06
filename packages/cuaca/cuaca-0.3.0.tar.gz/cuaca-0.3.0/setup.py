# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cuaca']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.28.1,<3.0.0']

setup_kwargs = {
    'name': 'cuaca',
    'version': '0.3.0',
    'description': 'A python wrapper for Malaysian Weather Service API',
    'long_description': None,
    'author': 'sweemeng',
    'author_email': 'sweester@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
