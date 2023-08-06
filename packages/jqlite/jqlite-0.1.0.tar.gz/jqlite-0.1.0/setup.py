# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jqlite']

package_data = \
{'': ['*']}

install_requires = \
['typer[all]>=0.6.1,<0.7.0']

entry_points = \
{'console_scripts': ['jqlite = jqlite.cli:main']}

setup_kwargs = {
    'name': 'jqlite',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'Christian',
    'author_email': 'xian.tuxoid@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
