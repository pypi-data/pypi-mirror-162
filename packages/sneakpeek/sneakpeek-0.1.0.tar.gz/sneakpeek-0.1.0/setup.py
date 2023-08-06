# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sneakpeek']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'sneakpeek',
    'version': '0.1.0',
    'description': 'A python module to generate link previews.',
    'long_description': '\n<div align="center">\n  <h1>\n    SneakPeek\n  </h1>\n  <h4>A python module and a minimalistic server to generate link previews.</h4>\n</div>\n\n\n',
    'author': 'Ameya Shenoy',
    'author_email': 'shenoy.ameya@gmail.com',
    'maintainer': 'Ameya Shenoy',
    'maintainer_email': 'shenoy.ameya@gmail.com',
    'url': 'https://github.com/codingcoffee/sneakpeek',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
