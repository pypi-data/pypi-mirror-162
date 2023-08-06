# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gqlient']

package_data = \
{'': ['*'], 'gqlient': ['templates/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'gql[aiohttp,requests]>=3.4.0,<4.0.0',
 'inflection>=0.5.1,<0.6.0',
 'typer>=0.4.2,<0.5.0']

setup_kwargs = {
    'name': 'graphqlient',
    'version': '0.0.1a2',
    'description': ':)',
    'long_description': 'None',
    'author': 'Vojtěch Dohnal',
    'author_email': 'vojdoh@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
