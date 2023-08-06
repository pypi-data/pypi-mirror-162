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
    'version': '0.1.3',
    'description': '',
    'long_description': '# slack_transfer\n[![python](https://img.shields.io/pypi/pyversions/slack-transfer.svg)](https://pypi.org/project/slack-transfer)\n[![pypi](https://img.shields.io/pypi/v/slack-transfer.svg)](https://pypi.org/project/slack-transfer)\n[![CI](https://github.com/masanorihirano/slack_transfer/actions/workflows/ci.yml/badge.svg)](https://github.com/masanorihirano/slack_transfer/actions/workflows/ci.yml)\n[![downloads](https://img.shields.io/pypi/dm/slack-transfer)](https://pypi.org/project/slack-transfer)\n[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Codacy Badge](https://app.codacy.com/project/badge/Grade/d8c6e7691ae4462592be32394699b09c)](https://www.codacy.com/gh/masanorihirano/slack_transfer/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=masanorihirano/slack_transfer&amp;utm_campaign=Badge_Grade)\n\n## Documentations & User Guides\nslack_transfer is a tool for transferring messages to the other slack workspace.\n\nDocumentations are available on [readthedoc](https://slack-transfer.readthedocs.io).\n-   [User guide (en)](https://slack-transfer.readthedocs.io/en/latest/user_guide/index.html)\n-   [ユーザーガイド (日本語)](https://slack-transfer.readthedocs.io/en/latest/user_guide/index_ja.html)\n\n## Install\nThis package is available on pypi as [`slack-transfer`](https://pypi.org/project/slack-transfer/)\n```bash\n$ pip install slack-transfer\n$ python\n>> import slack_transfer\n```\nPlease note that you have to user `slack_transfer` instead of `slack-transfer` for importing.\n\n## Issues and Contribution\nAbout issues (bugs):\n-   You can report issues [here](https://github.com/masanorihirano/slack_transfer/issues).\n-   日本語でissueを立てて構いません．\n-   There are no guarantee to support or fix those issues.\n\nContributions:\n-   You can send pull requests (PRs) to this repository.\n-   But, there are no guarantee to merge your PRs.\n',
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
