# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slack_transfer', 'slack_transfer.cli', 'slack_transfer.functions']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.28.1,<3.0.0',
 'slack-sdk>=3.18.1,<4.0.0',
 'tqdm>=4.64.0,<5.0.0']

setup_kwargs = {
    'name': 'slack-transfer',
    'version': '0.1.3a0',
    'description': '',
    'long_description': '# slack_transfer',
    'author': 'Masanori HIRANO',
    'author_email': 'masa.hirano.1996@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
