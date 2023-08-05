# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_autohelp']

package_data = \
{'': ['*']}

install_requires = \
['logzero>=1.7.0,<2.0.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0-alpha.16,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-autohelp',
    'version': '0.1.6',
    'description': 'nonebot2 plugin 自动生成载入插件的帮助信息，响应 /help !help help 菜单 caidan /i',
    'long_description': '# nonebot-plugin-autohelp\n[![nonebot2beta](https://img.shields.io/static/v1?label=nonebot&message=v2b2&color=green)](https://v2.nonebot.dev/)[![onebot](https://img.shields.io/static/v1?label=driver&message=onebot&color=green)](https://adapter-onebot.netlify.app/)[![python](https://img.shields.io/static/v1?label=python+&message=3.7%2B&color=blue)](https://img.shields.io/static/v1?label=python+&message=3.7%2B&color=blue)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/nonebot_plugin_autohelp.svg)](https://badge.fury.io/py/nonebot_plugin_autohelp)\n\nShow a summary of commands, aliases and usages for plugins loaded\n\n## Dependent adapter\n`onebotv11`\n\n## Install it\n\n```shell\npip install nonebot-plugin-autohelp\n# or poetry add nonebot-plugin-autohelp\n# pip install git+htts://github.com/ffreemt/nonebot-plugin-autohelp\n# poetry add git+htts://github.com/ffreemt/nonebot-plugin-autohelp\n\n# To upgrade\npip install nonebot-plugin-autohelp -U\n# or poetry add nonebot-plugin-autohelp@latest\n```\n\n## Use it\n```python\n# bot.py\nimport nonebot\nfrom nonebot.adapters.onebot.v11 import Adapter\n...\nnonebot.init()\n\ndriver = nonebot.get_driver()\ndriver.register_adapter(Adapter)\n\nnonebot.load_from_toml("pyproject.toml")\nnonebot.load_builtin_plugin("echo")\nnonebot.load_plugin("nonebot_plugin_guess")\n\nnonebot.load_plugin("nonebot_plugin_autohelp")\n\n# plugin loaded after autohelp will not be taken care of by autohelp\nnonebot.load_plugin("nonebot_plugin_fancy")\n\n```\n\nSample session in a qq group\n```bash\nmu (μ)(41947782)  11:23:34 AM\nhelp\nmubot(2129462094)  11:23:36 AM\nnickname:\ncommand_start: /\ncommand_sep: .\n\ncommand: say\ncommand: mecho\n\taliases: ping, ryt, 在不, p\n\ncommand: news\n\taliases: xinwen, 新闻, 无聊\n\ncommand: debug test: %s\n\taliases: 爬, fetch, crawl\n\ncommand: guess\n\taliases: cai, 猜猜看, 猜\n\n(help -d will display detailed docs for all plugins loaded before nonebot_plugin_autohelp)\n\nmu (μ)(41947782)  11:53:25 AM\nhelp -h\nmubot(2129462094)  11:53:27 AM\nusage: help [-h] [-d] [params [params ...]]\n\npositional arguments:\n  params         list of parameters of type str (default: None)\n\noptional arguments:\n  -h, --help     show this help message and exit\n  -d, --details  show __doc__ for each plugin (default: False)\n---\n\nmu (μ)(41947782)  11:23:34 AM\nhelp --details  # or help details\n...(attach __doc___ for each plugin, ommitted)\n```\n\n',
    'author': 'ffreemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/nonebot-plugin-autohelp',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
