# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['checkbox_api',
 'checkbox_api.client',
 'checkbox_api.methods',
 'checkbox_api.storage']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT>=1.7.1,<2.0.0', 'httpx==0.13.3']

setup_kwargs = {
    'name': 'checkbox-api',
    'version': '0.1.29',
    'description': 'checkbox.in.ua Transactional Processing API Client',
    'long_description': None,
    'author': 'Oleksandr Onufriichuk',
    'author_email': 'oleksandr.onufriichuk@itvaan.com.ua',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
