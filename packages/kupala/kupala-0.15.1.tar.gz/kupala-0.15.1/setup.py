# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kupala',
 'kupala.cache',
 'kupala.cache.backends',
 'kupala.console',
 'kupala.http',
 'kupala.http.middleware',
 'kupala.i18n',
 'kupala.security',
 'kupala.storages']

package_data = \
{'': ['*'], 'kupala': ['templates/errors/*']}

install_requires = \
['Babel>=2.9,<3.0',
 'Jinja2>=3.1,<4.0',
 'click>=8.1,<9.0',
 'deesk>=0.1,<0.2',
 'imia>=0.5,<0.6',
 'mailers>=2.0,<3.0',
 'passlib>=1.7,<2.0',
 'pydantic>=1.9,<2.0',
 'python-dotenv>=0.20,<0.21',
 'python-multipart>=0.0,<0.1',
 'starception>=0.3.1,<0.4.0',
 'starlette>=0.20,<0.21',
 'starsessions>=1.3,<2.0',
 'toronado>=0.1,<0.2']

extras_require = \
{'msgpack': ['msgpack>=1.0,<2.0'],
 'redis': ['aioredis>=2.0,<3.0'],
 's3': ['aioboto3>=9.4,<10.0']}

setup_kwargs = {
    'name': 'kupala',
    'version': '0.15.1',
    'description': 'A modern web framework for Python.',
    'long_description': '# Kupala Framework\n\nA modern web framework for Python.\n\n![PyPI](https://img.shields.io/pypi/v/kupala)\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/alex-oleshkevich/kupala/Lint)\n![GitHub](https://img.shields.io/github/license/alex-oleshkevich/kupala)\n![Libraries.io dependency status for latest release](https://img.shields.io/librariesio/release/pypi/kupala)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/kupala)\n![GitHub Release Date](https://img.shields.io/github/release-date/alex-oleshkevich/kupala)\n![Lines of code](https://img.shields.io/tokei/lines/github/alex-oleshkevich/kupala)\n\n## Installation\n\nInstall `kupala` using PIP or poetry:\n\n```bash\npip install kupala\n# or\npoetry add kupala\n```\n\n## Features\n\n-   TODO\n\n## Quick start\n\nSee example application in `examples/` directory of this repository.\n',
    'author': 'Alex Oleshkevich',
    'author_email': 'alex.oleshkevich@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alex-oleshkevich/kupala',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
