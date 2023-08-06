# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sqlalchemy_file']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4,<1.5.0', 'apache-libcloud>=3.6.0,<4.0.0']

setup_kwargs = {
    'name': 'sqlalchemy-file',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'jowilf',
    'author_email': 'hounonj@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
