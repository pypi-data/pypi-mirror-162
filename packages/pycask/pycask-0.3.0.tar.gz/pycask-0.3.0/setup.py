# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pycask']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'pycask',
    'version': '0.3.0',
    'description': 'A Log-Structured KV Store based on bitcask, written in Python.',
    'long_description': '# PyCask\n\nA Log-Structured KV Store based on [bitcask](https://riak.com/assets/bitcask-intro.pdf), written in Python.\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n## Table of Contents\n\n- [Requirements](#requirements)\n- [License](#license)\n\n## Requirements\n\nPython 3.9+\n\n## License\n\n[MIT @ Huang Kai](./LICENSE)\n',
    'author': 'huangkai',
    'author_email': 'h1770360848@outlook.com',
    'maintainer': 'huangkai',
    'maintainer_email': 'h1770360848@outlook.com',
    'url': 'https://github.com/Huangkai1008/pycask',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
