# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vyper_tree']

package_data = \
{'': ['*']}

install_requires = \
['vyper @ git+https://github.com/vyperlang/vyper@master']

setup_kwargs = {
    'name': 'vyper-tree',
    'version': '0.1.0',
    'description': '',
    'long_description': None,
    'author': 'z80',
    'author_email': 'z80@ophy.xyz',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/z80dev/vyper-tree',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<3.11',
}


setup(**setup_kwargs)
