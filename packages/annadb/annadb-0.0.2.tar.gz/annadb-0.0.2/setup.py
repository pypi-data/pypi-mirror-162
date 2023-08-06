# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['annadb',
 'annadb.data_types',
 'annadb.query',
 'annadb.query.delete',
 'annadb.query.find',
 'annadb.query.get',
 'annadb.query.insert',
 'annadb.query.limit',
 'annadb.query.offset',
 'annadb.query.sort',
 'annadb.query.update',
 'annadb.shell']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.1.3,<9.0.0',
 'pyzmq>=23.1.0,<24.0.0',
 'textual>=0.1.18,<0.2.0',
 'tyson>=0.1.5,<0.2.0']

entry_points = \
{'console_scripts': ['annadb = annadb.shell:shell']}

setup_kwargs = {
    'name': 'annadb',
    'version': '0.0.2',
    'description': 'AnnaDB driver and shell',
    'long_description': None,
    'author': 'Roman Right',
    'author_email': 'roman-right@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
