# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rxio']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'rxio',
    'version': '0.1.0',
    'description': 'Flexible, predictable, async reactive programming in modern Python',
    'long_description': '# Reactive I/O\n\n-----\n\n[![PyPI version shields.io](https://img.shields.io/pypi/v/rxio.svg)](https://pypi.python.org/pypi/rxio/)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rxio.svg)](https://pypi.python.org/pypi/rxio/)\n[![PyPI license](https://img.shields.io/pypi/l/rxio.svg)](https://pypi.python.org/pypi/rxio/)\n\n-----',
    'author': 'Joren Hammudoglu',
    'author_email': 'jhammudoglu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jorenham/rxio',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
