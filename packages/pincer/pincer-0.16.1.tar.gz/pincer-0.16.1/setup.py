# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pincer',
 'pincer.commands',
 'pincer.commands.components',
 'pincer.core',
 'pincer.middleware',
 'pincer.objects',
 'pincer.objects.app',
 'pincer.objects.events',
 'pincer.objects.guild',
 'pincer.objects.message',
 'pincer.objects.user',
 'pincer.objects.voice',
 'pincer.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0']

extras_require = \
{'img': ['Pillow>=9.2.0,<10.0.0', 'types-Pillow>=9.2.1,<10.0.0'],
 'speed': ['orjson>=3.7.11,<4.0.0',
           'Brotli>=1.0.9,<2.0.0',
           'aiodns>=3.0.0,<4.0.0',
           'cchardet>=2.1.7,<3.0.0']}

setup_kwargs = {
    'name': 'pincer',
    'version': '0.16.1',
    'description': 'Discord API wrapper rebuilt from scratch.',
    'long_description': '# Pincer\n\n[![PyPI - Downloads](https://img.shields.io/badge/dynamic/json?label=downloads&query=%24.total_downloads&url=https%3A%2F%2Fapi.pepy.tech%2Fapi%2Fprojects%2FPincer)](https://pypi.org/project/Pincer)\n![PyPI](https://img.shields.io/pypi/v/Pincer)\n![PyPI - Format](https://img.shields.io/pypi/format/Pincer)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Pincer)\n[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/Pincer-org/pincer/badges/quality-score.png?b=main)](https://scrutinizer-ci.com/g/Pincer-org/pincer/?branch=main)\n[![Build Status](https://scrutinizer-ci.com/g/Pincer-org/Pincer/badges/build.png?b=main)](https://scrutinizer-ci.com/g/Pincer-org/Pincer/build-status/main)\n[![Documentation Status](https://readthedocs.org/projects/pincer/badge/?version=latest)](https://pincer.readthedocs.io/en/latest/?badge=latest)\n[![codecov](https://codecov.io/gh/Pincer-org/Pincer/branch/main/graph/badge.svg?token=T15T34KOQW)](https://codecov.io/gh/Pincer-org/Pincer)\n![Lines of code](https://tokei.rs/b1/github/pincer-org/pincer?category=code&path=pincer)\n![Repo Size](https://img.shields.io/github/repo-size/Pincer-org/Pincer)\n![GitHub last commit](https://img.shields.io/github/last-commit/Pincer-org/Pincer)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/Pincer-org/Pincer?label=commits)\n![GitHub](https://img.shields.io/github/license/Pincer-org/Pincer)\n![Discord](https://img.shields.io/discord/881531065859190804)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n![gitmoji](https://img.shields.io/badge/gitmoji-%20🚀%20💀-FFDD67.svg)\n\n## :pushpin: Links\n\n> <img src="../assets/svg/discord.svg" width="16px" alt="Discord Logo"> ｜Join the Discord server: https://discord.gg/pincer <br>\n> <img src="../assets/svg/pypi.svg" width="16px" alt="PyPI Logo"> ｜The PyPI package: https://pypi.org/project/Pincer <br>\n> <img src="../assets/svg/pincer.svg" width="16px" alt="Pincer Logo"> ｜Our website: https://pincer.dev <br>\n> 📝 | ReadTheDocs: https://pincer.readthedocs.io\n\n## ☄️ Installation\n\nUse the following command to install Pincer into your Python environment:\n\n```sh\npip install pincer\n```\n\nTo install our version with Aiohttp Speedup, use:\n\n```sh\npip install pincer[speed]\n```\n\n<details>\n\n<summary>\n    ⚙️ <i> Didn\'t work?</i>\n</summary>\n\nDepending on your Python installation, you might need to use one of the\nfollowing:\n\n- Python is not in PATH\n\n    ```sh\n    path/to/python.exe -m pip install pincer\n    ```\n\n- Python is in PATH but pip is not\n\n    ```sh\n    python -m pip install pincer\n    ```\n\n- Unix systems can use pip3/python3 commands\n\n    ```sh\n    pip3 install pincer\n    ```\n\n    ```sh\n    python3 -m pip install pincer\n    ```\n\n- Using multiple Python versions\n\n    ```sh\n    py -m pip install pincer\n    ```\n\n</details>\n\n**Client base class example:**\n\n```py\nfrom pincer.client import Bot\n\n# Note that both `Bot` and `Client` are valid!\nbot = Bot("YOUR_TOKEN_HERE")\nbot.run()\n```\n\n**An example on the `on_ready` event**\n\nPincer bots are required to inherit from the Client.\n\n```py\nfrom time import perf_counter\nfrom pincer import Client\n\nmarker = perf_counter()\n\n\nclass Bot(Client):\n\n    @Client.event\n    async def on_ready():\n        print(f"Logged in as {client.bot} after {perf_counter() - marker} seconds")\n\n\nclient = Bot("YOUR_TOKEN_HERE")\nclient.run()\n```\n\n### Interactions\n\nPincer makes developing application commands intuitive and fast.\n\n```py\nfrom typing import Annotation  # python 3.9+\nfrom typing_extensions import Annotation  # python 3.8\n\nfrom pincer import Client\nfrom pincer.commands import command, CommandArg, Description\nfrom pincer.objects import UserMessage, User\n\n\nclass Bot(Client):\n    @Client.event\n    async def on_ready(self) -> None:\n        ...\n\n    @command(description="Say something as the bot!")\n    async def say(self, message: str):\n        return message\n\n    @user_command\n    async def user_command(self, user: User):\n        return f"The user is {user}"\n\n    @message_command(name="Message command")\n    async def message_command(self, message: UserMessage):\n        return f"The message read \'{message.content}\'"\n\n    @command(description="Add two numbers!")\n    async def add(\n        self,\n        first: Annotation[int, Description("The first number")],\n        second: Annotation[int, Description("The second number")]\n    ):\n        return f"The addition of `{first}` and `{second}` is `{first + second}`"\n\n\n```\n\nFor more examples, you can take a look at the examples folder or check out our\nbot:\n\n> <https://github.com/Pincer-org/Pincer-bot>\n\nYou can also read the interactions guide for more information:\n> <https://docs.pincer.dev/en/latest/interactions.html>\n\n### Advanced Usage\n\n#### Enable the debug mode\n\n_If you want to see everything that is happening under the hood, either out of\ncuriosity or to get a deeper insight into the implementation of some features,\nwe provide debug logging!_\n\n```py\nimport logging\n\nlogging.basicConfig(level=logging.DEBUG)\n```\n\n#### Middleware\n\n_The middleware system was introduced in version `0.4.0-dev`. This system gives you the\nfreedom to create custom events and remove the already existing middleware created by\nthe developers. Your custom middleware directly receives the payload from\nDiscord. You can\'t do anything wrong without accessing the `override` attribute, but if\nyou do access it, the Pincer team will not provide any support for weird behavior.\nSo, in short, only use this if you know what you\'re doing. An example of using\nthe middleware system with a custom `on_ready` event can be found\n[in our docs](https://pincer.readthedocs.io/en/latest/pincer.html#pincer.client.middleware).\n._\n\n## 🏷️ License\n\n`© 2021 copyright Pincer`\n\nThis repository is licensed under the MIT License.\n\nSee LICENSE for details.\n',
    'author': 'Pincer-org',
    'author_email': 'contact@pincer.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pincer.dev',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
