# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qctrlqua']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.18,<2.0', 'toml>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'qctrl-qua',
    'version': '0.2.1',
    'description': 'Q-CTRL Python QUA',
    'long_description': '# Q-CTRL Python QUA\n\nThe Q-CTRL Python QUA package allows you to integrate Boulder Opal with the QUA\nquantum computing language.\n',
    'author': 'Q-CTRL',
    'author_email': 'support@q-ctrl.com',
    'maintainer': 'Q-CTRL',
    'maintainer_email': 'support@q-ctrl.com',
    'url': 'https://q-ctrl.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
