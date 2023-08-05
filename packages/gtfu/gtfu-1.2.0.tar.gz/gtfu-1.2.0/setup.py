# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gtfu']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'lxml>=4.8.0,<5.0.0',
 'pyperclip>=1.8.2,<2.0.0',
 'readchar>=3.0.5,<4.0.0',
 'requests>=2.27.1,<3.0.0',
 'rich>=12.0.1,<13.0.0']

entry_points = \
{'console_scripts': ['gtfu = gtfu.__main__:main']}

setup_kwargs = {
    'name': 'gtfu',
    'version': '1.2.0',
    'description': 'Command line tool to Get pageTitle From Url.',
    'long_description': '# gtfu\n\n[日本語](https://github.com/seijinrosen/gtfu/blob/main/README.ja.md) |\n[English](https://github.com/seijinrosen/gtfu/blob/main/README.md)\n\n[![PyPI](https://img.shields.io/pypi/v/gtfu)](https://pypi.python.org/pypi/gtfu)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gtfu)](https://pypi.python.org/pypi/gtfu)\n[![Tests](https://github.com/seijinrosen/gtfu/actions/workflows/tests.yml/badge.svg)](https://github.com/seijinrosen/gtfu/actions/workflows/tests.yml)\n[![CodeQL](https://github.com/seijinrosen/gtfu/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/seijinrosen/gtfu/actions/workflows/codeql-analysis.yml)\n[![codecov](https://codecov.io/gh/seijinrosen/gtfu/branch/main/graph/badge.svg)](https://codecov.io/gh/seijinrosen/gtfu)\n[![Downloads](https://pepy.tech/badge/gtfu)](https://pepy.tech/project/gtfu)\n[![Downloads](https://pepy.tech/badge/gtfu/month)](https://pepy.tech/project/gtfu)\n[![Downloads](https://pepy.tech/badge/gtfu/week)](https://pepy.tech/project/gtfu)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\nCommand line tool to Get pageTitle From Url.\n\n## Installation\n\nIt supports Python 3.7+.\n\n```sh\npip install gtfu\n```\n\n## Usage\n\nAfter installation, type the following command into your terminal application.\n\n### Standard mode\n\n```sh\ngtfu https://example.com/\n```\n\nThe page title will be copied to the clipboard.\n\n- `Example Domain`\n\n### Markdown mode\n\n```sh\ngtfu -m https://example.com/\n```\n\nThe page title will be copied to the clipboard in markdown format.\n\n- `[Example Domain](https://example.com/)`\n\n### Prompt mode\n\n```sh\ngtfu\n```\n\nAn interactive prompt will begin. You will be asked for the URL to be retrieved and whether you want it in Markdown format.\n',
    'author': 'seijinrosen',
    'author_email': '86702775+seijinrosen@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/seijinrosen',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
