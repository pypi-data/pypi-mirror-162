# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['whatsapie',
 'whatsapie.ext',
 'whatsapie.ext.message',
 'whatsapie.schema_generator']

package_data = \
{'': ['*']}

install_requires = \
['httpx>=0.23.0,<0.24.0']

setup_kwargs = {
    'name': 'whatsapie',
    'version': '0.1.8',
    'description': "Unofficial Python wrapper for Meta's whatsapp cloud API",
    'long_description': None,
    'author': 'Aadil Varsh',
    'author_email': 'aadilvarshofficial@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
