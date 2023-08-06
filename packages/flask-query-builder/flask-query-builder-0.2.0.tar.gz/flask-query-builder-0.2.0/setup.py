# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['flask_query_builder']

package_data = \
{'': ['*']}

install_requires = \
['Flask', 'SQLAlchemy==1.4.0']

setup_kwargs = {
    'name': 'flask-query-builder',
    'version': '0.2.0',
    'description': 'A request query builder for flask and sqlalchemy',
    'long_description': None,
    'author': 'Demos Petsas',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*',
}


setup(**setup_kwargs)
