# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['phrase_translator']

package_data = \
{'': ['*']}

install_requires = \
['wn>=0.9.1,<0.10.0']

setup_kwargs = {
    'name': 'phrase-translator',
    'version': '0.1.2',
    'description': 'A very simple package to translate single words and phrases between different languages.',
    'long_description': '### Phrase Translator\n\nA very simple package to translate single words and phrases between different languages.\n\n[![PyPI Version][pypi-image]][pypi-url]\n[![Build Status][build-image]][build-url]\n[![Versions][versions-image]][versions-url]\n\n...\n\n<!-- Badges: -->\n\n[pypi-image]: https://img.shields.io/pypi/v/phrase-translator\n[pypi-url]: https://pypi.org/project/phrase-translator/\n[build-image]: https://github.com/fr2501/phrase-translator/actions/workflows/build.yaml/badge.svg\n[build-url]: https://github.com/fr2501/phrase-translator/actions/workflows/build.yaml\n[versions-image]: https://img.shields.io/pypi/pyversions/phrase-translator/\n[versions-url]: https://pypi.org/project/phrase-translator/\n',
    'author': 'Fabian Richter',
    'author_email': 'me@fr2501.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
