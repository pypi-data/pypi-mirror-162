# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['trex']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.27,<4.0.0',
 'requests>=2.28.1,<3.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['trex = trex.main:app']}

setup_kwargs = {
    'name': 'trex',
    'version': '0.1.6',
    'description': 'Templatosaurus Rex 🦖 Create and manage project templates in your terminal',
    'long_description': '<img alt="trex Logo" src="https://cdn.berrysauce.me/assets/trex-banner.jpg">\n<p align="center"><strong>Templatosaurus Rex: Create and manage project templates in your terminal 🦖</strong></p>\n<p align="center">\n    <img alt="GitHub repo size" src="https://img.shields.io/github/repo-size/berrysauce/trex?label=size">\n    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/berrysauce/trex">\n    <img alt="GitHub CodeQL" src="https://github.com/berrysauce/trex/actions/workflows/codeql-analysis.yml/badge.svg">\n    <img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/trex?label=PyPi%20downloads">\n    <img alt="PyPI" src="https://img.shields.io/pypi/v/trex">\n    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/trex">\n</p>\n\n---\n\n## 🦖 What is trex?\ntrex is a template manager in the form of a CLI app. You can create, organize, and clone-from template directories. It doesn’t matter if the template is a directory on your machine or a GitHub repository: with trex you only need a few seconds to actually get to coding. Not only that, but trex is really easy to use.\n\n## 🚧 Features and Roadmap\n- [x] Organise templates (create, remove, list)\n- [x] Make project from local directory template\n- [ ] Make project from GitHub template  \n- [x] Create git repository on creation\n- [ ] Run scripts automatically on creation\n- [x] Create virtualenv automatically and import requirements on creation\n\n→ Do you have any feature requests? [Submit them here](https://github.com/berrysauce/trex/issues).\n\n## ☁️ Install trex\n**Make sure you have Python 3.9 or above installed on your system.**\n\ntrex is available on PyPi and can be installed via pip with the following command:\n```\npip install trex\n```\nCheck if the installation was successful:\n```\ntrex version\n```\n\n## 📘 Documentation\nRead more here → https://berrysauce.me/trex\n\n## 📜 License\n\ntrex: A modern and intuitive templating CLI\nCopyright (C) 2022 berrysauce (Paul Haedrich)\n\nThis program is free software: you can redistribute it and/or modify\nit under the terms of the GNU General Public License as published by\nthe Free Software Foundation, either version 3 of the License, or\n(at your option) any later version.\n\nThis program is distributed in the hope that it will be useful,\nbut WITHOUT ANY WARRANTY; without even the implied warranty of\nMERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\nGNU General Public License for more details.\n\nYou should have received a copy of the GNU General Public License\nalong with this program.  If not, see <https://www.gnu.org/licenses/>.\n\nFor legal questions, contact legal[at]berrysauce[dot]me.\n\n<a href="https://deta.sh/?ref=basketball" target="_blank"><img src="https://cdn.berrysauce.me/assets/deta-sponsor-banner.jpg" alt="Sponsored by Deta"></a>\n',
    'author': 'Paul Haedrich',
    'author_email': 'paul@berrysauce.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://berrysauce.me/trex',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
