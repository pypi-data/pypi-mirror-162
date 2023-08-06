# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hyperutils', 'hyperutils.models']

package_data = \
{'': ['*']}

install_requires = \
['PyJWT[crypto]>=2.4.0,<3.0.0',
 'fastapi',
 'pydantic[email]>=1.9.1,<2.0.0',
 'pymongo>=4.1.1,<5.0.0']

setup_kwargs = {
    'name': 'hyperutils',
    'version': '0.1.8',
    'description': 'hyperbloq-utils',
    'long_description': None,
    'author': 'Lionel Cuevas',
    'author_email': 'lionel.c@hyperbloq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
