# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['uoshardware', 'uoshardware.interface']

package_data = \
{'': ['*']}

install_requires = \
['pylint>=2.14.4,<3.0.0', 'pyserial>=3.5,<4.0']

setup_kwargs = {
    'name': 'uos-hardware',
    'version': '0.1.0',
    'description': 'A hardware abstraction layer for microcontrollers running UOS compliant firmware.',
    'long_description': None,
    'author': 'nulltek',
    'author_email': 'steve.public@nulltek.xyz',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
