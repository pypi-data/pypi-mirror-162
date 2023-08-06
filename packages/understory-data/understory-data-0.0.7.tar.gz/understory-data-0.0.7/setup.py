# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['understory', 'understory.data', 'understory.data.templates']

package_data = \
{'': ['*']}

install_requires = \
['understory>=0.0,<0.1']

setup_kwargs = {
    'name': 'understory-data',
    'version': '0.0.7',
    'description': '',
    'long_description': None,
    'author': 'Angelo Gladding',
    'author_email': 'angelo@ragt.ag',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
