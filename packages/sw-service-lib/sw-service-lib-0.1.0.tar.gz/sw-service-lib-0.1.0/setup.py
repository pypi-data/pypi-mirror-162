# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sw_service_lib']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0',
 'gql[all]>=3.3.0,<4.0.0',
 'rich>=12.4.4,<13.0.0',
 'sgqlc>=16.0,<17.0']

setup_kwargs = {
    'name': 'sw-service-lib',
    'version': '0.1.0',
    'description': 'Python library for Strangeworks services to interact with the Strangeworks Platform',
    'long_description': None,
    'author': 'Strangeworks Devs',
    'author_email': 'hello@strangeworks.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
