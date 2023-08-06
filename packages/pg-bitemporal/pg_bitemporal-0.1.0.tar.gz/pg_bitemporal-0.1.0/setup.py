# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pg_bitemporal', 'pg_bitemporal.django', 'pg_bitemporal.sqlalchemy']

package_data = \
{'': ['*']}

install_requires = \
['Django>=4.0.4,<5.0.0', 'SQLAlchemy>=1.4.32,<2.0.0', 'psycopg2>=2.9.3,<3.0.0']

setup_kwargs = {
    'name': 'pg-bitemporal',
    'version': '0.1.0',
    'description': 'Define and interface with bitemporal data models in postgres',
    'long_description': None,
    'author': 'Adam',
    'author_email': 'adamsanghera@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
