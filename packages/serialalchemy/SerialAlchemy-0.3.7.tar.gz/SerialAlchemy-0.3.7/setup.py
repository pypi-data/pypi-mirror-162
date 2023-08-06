# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['serialalchemy']

package_data = \
{'': ['*']}

install_requires = \
['sqlalchemy>=1.4.0,<2.0.0']

setup_kwargs = {
    'name': 'serialalchemy',
    'version': '0.3.7',
    'description': 'Mixin for serializing SQLAlchemy ORM classes into dict or json',
    'long_description': None,
    'author': 'Matt Schmidt',
    'author_email': 'sloatx@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
