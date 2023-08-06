# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['usernado']

package_data = \
{'': ['*']}

install_requires = \
['pendulum>=2.1.2,<3.0.0', 'tornado-debugger>=0.9.0,<0.10.0']

setup_kwargs = {
    'name': 'usernado',
    'version': '0.3',
    'description': 'Makes it Easy to Manage Tornado Applications',
    'long_description': '<a id="top"></a>\n<br />\n\n<div align="center">\n  <h1>Usernado</h1>\n  <p align="center">\n    Makes it Easy to Manage Tornado :tornado: Applications\n    <br />\n    <a href="https://usernado.readthedocs.io/en/latest/"><strong>Explore the docs »</strong></a>\n    <br />\n    <br />\n    <a href="https://github.com/reganto/usernado/actions?query=workflow%3ALinters+event%3Apush+branch%3Amaster" target="_blank">\n    <img src="https://github.com/reganto/usernado/workflows/Linters/badge.svg?event=push&branch=master" alt="Test">\n    </a>\n    <a href="https://github.com/reganto/Usernado/issues"><img src="https://img.shields.io/github/issues/reganto/usernado"></a> <a href="https://github.com/reganto/usernado/blob/master/LICENSE.txt"><img src="https://img.shields.io/github/license/reganto/usernado"></a>  <a href="https://badge.fury.io/py/usernado"><img src="https://badge.fury.io/py/usernado.svg" alt="PyPI version" height="18"></a> <a href="https://pepy.tech/project/usernado"><img src="https://pepy.tech/badge/usernado"/></a>\n  </p>\n</div>\n\n<!-- Why Userndo  -->\n\n## Why Usernado\n\nI\'m using 🌪️ every day. I really like it 😍 . Besides of all advantages of Tornado, it\'s not a full-stack framework, and I had to put all the pieces of the puzzle together every day 😩! So this is my attempt to follow DRY(Don\'t Repeat Yourself) principle. This is how the Usernado was born.\n\n<!-- Features -->\n\n## Features\n\n- REST support :zap:\n\n- Websocket easier than ever :zap:\n\n- ORM agnostic authentication :zap:\n\n- Humanize datetime in templates :zap:\n\n- Better exception printer thanks to [tornado-debugger](https://github.com/bhch/tornado-debugger) :zap:\n\n<!-- Getting Started -->\n\n## Installation\n\nInstall either with pip or poetry.\n\n```bash\npip install usernado\n```\n```bash\npoetry add usernado\n```\n\nOr optionally you can install from github using \n```bash \npip install git+https://github.com/reganto/usernado\n```\n\n<!-- USAGE EXAMPLES -->\n\n## Usage\n\n### Example\n\n```python\nfrom usernado import Usernado\n\n\nclass HelloHandler(Usernado.Web):\n    def get(self):\n        self.write("Hello, World!")\n```\n\nFor more examples please Check out [examples](https://github.com/reganto/Usernado/tree/master/example).\n\n<!-- ROADMAP -->\n\n## Roadmap\n\n- [x] Send and broadcast for websockets\n- [x] Abstracted authentication methods\n- [x] Authenticaion methods should return True/False\n- [x] Add diff_for_human (humanize) decorator\n- [x] Add api_route for API handlers\n- [x] Add username & password to test login \n- [x] Add pluralize (str_plural) uimodule\n- [x] Add pagination [:link:](https://github.com/reganto/tornado-pagination)\n\n<!-- CONTACT -->\n\n## Contact\n\nEmail: tell.reganto[at]gmail[dot]com\n\n<p align="right"><a href="#top"><img src="https://raw.githubusercontent.com/DjangoEx/python-engineer-roadmap/main/statics/top.png" width=50 height=50 /></a></p>\n',
    'author': 'Reganto',
    'author_email': 'tell.reganto@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/reganto/usernado',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
