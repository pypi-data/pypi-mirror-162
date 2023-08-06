# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['goodmap', 'goodmap.db']

package_data = \
{'': ['*'], 'goodmap': ['static/*', 'templates/*']}

install_requires = \
['Babel>=2.10.3,<3.0.0',
 'Flask-Babel>=2.0.0,<3.0.0',
 'Flask>=2.1.1,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'google-cloud-storage>=2.3.0,<3.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'pytest>=7.1.2,<8.0.0']

setup_kwargs = {
    'name': 'goodmap',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Krzysztof Kolodzinski',
    'author_email': 'krzysztof.kolodzinski@problematy.pl',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
