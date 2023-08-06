# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['matrix_asgi']

package_data = \
{'': ['*']}

install_requires = \
['Markdown>=3.4.1,<4.0.0',
 'channels>=3.0.5,<4.0.0',
 'matrix-nio>=0.19.0,<0.20.0']

entry_points = \
{'console_scripts': ['matrix-asgi = matrix_asgi.__main__:main']}

setup_kwargs = {
    'name': 'matrix-asgi',
    'version': '0.2.3',
    'description': 'ASGI Server for the Matrix protocol',
    'long_description': None,
    'author': 'Guilhem Saurel',
    'author_email': 'guilhem.saurel@laas.fr',
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
