# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_guess']

package_data = \
{'': ['*']}

install_requires = \
['joblib>=1.0.1,<2.0.0',
 'logzero>=1.6.3,<2.0.0',
 'nonebot-adapter-onebot>=2.0.0-beta.1,<3.0.0',
 'nonebot2>=2.0.0-beta.2,<3.0.0',
 'pydantic[dotenv]>=1.8.1,<2.0.0',
 'pyquery>=1.4.3,<2.0.0',
 'pytz>=2021.1,<2022.0']

setup_kwargs = {
    'name': 'nonebot-plugin-guess',
    'version': '0.1.8',
    'description': 'nobebot2插件《猜猜看》',
    'long_description': '<!-- [![tests](https://github.com/ffreemt/nonebot-plugin-guess-game/actions/workflows/routine-tests.yml/badge.svg)](https://github.com/ffreemt/nonebot-plugin-guess-game/actions/workflows/routine-tests.yml) -->\n# nonebot-plugin-guess\n[![nonebot2beta](https://img.shields.io/static/v1?label=nonebot&message=v2b2&color=green)](https://v2.nonebot.dev/)[![onebot](https://img.shields.io/static/v1?label=driver&message=onebot&color=green)](https://adapter-onebot.netlify.app/)[![python](https://img.shields.io/static/v1?label=python+&message=3.7%2B&color=blue)](https://img.shields.io/static/v1?label=python+&message=3.7%2B&color=blue)[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![PyPI version](https://badge.fury.io/py/nonebot-plugin-guess.svg)](https://badge.fury.io/py/nonebot-plugin-guess)\n\n《猜猜看》nonebot2插件（Guess a name plugin for nonebot2）\n\nField-tested with ``nonebot 2.0.0b2``\n\n## 安装\n\n```bash\npip install nonebot-plugin-guess\n# pip install nonebot-plugin-guess -U  # 升级到最新版\n```\nor\n```bash\npoetry add nonebot-plugin-guess\n# poetry add nonebot-plugin-guess@latest   # 升级到最新版\n```\nor\n```\npoetry add git+https://github.com/ffreemt/nonebot-plugin-guess-game.git\n```\nor\n```\npip install git+https://github.com/ffreemt/nonebot-plugin-guess-game.git\n```\nor clone [https://github.com/ffreemt/nonebot-plugin-guess-game](https://github.com/ffreemt/nonebot-plugin-guess-game) and install from the repo.\n\n## 使用\n```python\n# bot.py\n...\nnonebot.load_plugin("nonebot_plugin_guess")\n...\n```\n然后在机器人所在的群里或给机器人发私信 `/guess` （或cai, 猜猜看, 猜）即可开始“猜猜看”游戏。\n\n### 定制\n\n插件自带的游戏数据仅限“猜城市名” 及固定的城市名："上海", "北京", "广州", "深圳", "香港", "雅典", "西安", "长沙", "多伦多", "旧金山", "Zurich", "约翰内斯堡"; 最多猜的次数： 4\n\n如需自己定制游戏，可在`.env` 里加入：\n```bash\n# .env\nguess_name = "人名"\nguess_max = 3\nguess_name_list = ["贾宝玉", "林黛玉"，]\n```',
    'author': 'freemt',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ffreemt/nonebot-plugin-guess-game',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
