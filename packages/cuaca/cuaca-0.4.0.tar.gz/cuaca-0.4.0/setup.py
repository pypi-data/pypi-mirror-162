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
    'version': '0.4.0',
    'description': 'A python wrapper for Malaysian Weather Service API',
    'long_description': '# cuaca aka the Malaysian Weather Service API Wrapper\n\nTo use the API first please register the API at https://api.met.gov.my/\n\nexample usage\n\n```python\nimport cuaca\n\napi = cuaca.WeatherAPI("API_KEY")\n\nlocations = api.locations("STATE")\nstates = api.states()\nstate = api.state("selangor")\n\nforecast = api.forecast("LOCATION:15", "2017-08-12", "2017-08-13")\n```\n',
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
