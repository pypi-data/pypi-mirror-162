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
    'version': '1.0.0',
    'description': 'ASGI Server for the Matrix protocol',
    'long_description': '# Matrix ASGI\n\n[![Tests](https://github.com/nim65s/matrix-asgi/actions/workflows/test.yml/badge.svg)](https://github.com/nim65s/matrix-asgi/actions/workflows/test.yml)\n[![Lints](https://github.com/nim65s/matrix-asgi/actions/workflows/lint.yml/badge.svg)](https://github.com/nim65s/matrix-asgi/actions/workflows/lint.yml)\n[![Release](https://github.com/nim65s/matrix-asgi/actions/workflows/release.yml/badge.svg)](https://pypi.org/project/matrix-asgi)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/nim65s/matrix-asgi/main.svg)](https://results.pre-commit.ci/latest/github/nim65s/matrix-asgi/main)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![codecov](https://codecov.io/gh/nim65s/matrix-asgi/branch/main/graph/badge.svg?token=75XO2X5QW0)](https://codecov.io/gh/nim65s/matrix-asgi)\n[![Maintainability](https://api.codeclimate.com/v1/badges/a0783da8c0461fe95eaf/maintainability)](https://codeclimate.com/github/nim65s/matrix-asgi/maintainability)\n[![PyPI version](https://badge.fury.io/py/matrix-asgi.svg)](https://badge.fury.io/py/matrix-asgi)\n\nwith [matrix-nio](https://github.com/poljar/matrix-nio)\n\n## Install\n\n```\npython3 -m pip install matrix-asgi\n```\n\n## Use it in your app\n\nYou can look at the [models.py](https://github.com/nim65s/matrix-asgi/blob/main/tests/django_app/models.py) and\n[consumers.py](https://github.com/nim65s/matrix-asgi/blob/main/tests/django_app/consumers.py) files in the test\napplication for a simple and quick example.\n\n## Start\n\nCreate a matrix user for the bot, and launch this server with the following arguments and/or environment variables\n(environment variables update defaults, arguments take precedence):\n\n```\nmatrix-asgi\n# OR\npython -m matrix_asgi\n```\n\n```\nusage: matrix-asgi [-h] [-u MATRIX_URL] -i MATRIX_ID -p MATRIX_PW [-v] application\n\nMatrix ASGI Server.\n\npositional arguments:\n  application           The ASGI application instance to use as path.to.module:application\n\noptions:\n  -h, --help            show this help message and exit\n  -u MATRIX_URL, --matrix-url MATRIX_URL\n                        matrix homeserver url. Default: `https://matrix.org`.\n                        Environment variable: `MATRIX_URL`\n  -i MATRIX_ID, --matrix-id MATRIX_ID\n                        matrix user-id. Required.\n                        Environment variable: `MATRIX_ID`\n  -p MATRIX_PW, --matrix-pw MATRIX_PW\n                        matrix password. Required.\n                        Environment variable: `MATRIX_PW`\n  -v, --verbose         increment verbosity level\n```\n\n## Unit tests\n\n```\ndocker compose -f test.yml up --exit-code-from tests --force-recreate --build\n```\n\n## JSON Specification\n\nref. [spec.md](https://github.com/nim65s/matrix-asgi/blob/main/spec.md)\n\n## Changes\n\nref. [CHANGELOG.md](https://github.com/nim65s/matrix-asgi/blob/main/CHANGELOG.md)\n',
    'author': 'Guilhem Saurel',
    'author_email': 'guilhem.saurel@laas.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nim65s/matrix-asgi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
