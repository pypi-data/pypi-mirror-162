# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['revolt', 'revolt.ext', 'revolt.ext.commands', 'revolt.types']

package_data = \
{'': ['*']}

install_requires = \
['aenum==3.1.8', 'aiohttp==3.7.4', 'typing-extensions==4.1.1', 'ulid-py==1.1.0']

extras_require = \
{'docs': ['Sphinx==4.3.2',
          'sphinx-nameko-theme==0.0.3',
          'sphinx-toolbox==2.15.2'],
 'speedups': ['ujson==5.1.0', 'msgpack']}

setup_kwargs = {
    'name': 'revolt.py',
    'version': '0.1.9',
    'description': 'Python wrapper for the revolt.chat API',
    'long_description': '# Revolt.py\n\nAn async library to interact with the https://revolt.chat API.\n\nYou can join the support server [here](https://rvlt.gg/FDXER6hr) and find the library\'s documentation [here](https://revoltpy.readthedocs.io/en/latest/).\n\n## Installing\n\nYou can use `pip` to install revolt.py. It differs slightly depending on what OS/Distro you use.\n\nOn Windows\n```\npy -m pip install -U revolt.py # -U to update\n```\n\nOn macOS and Linux\n```\npython3 -m pip install -U revolt.py\n```\n\n## Example\n\nMore examples can be found in the [examples folder](https://github.com/revoltchat/revolt.py/blob/master/examples).\n\n```py\nimport revolt\nimport asyncio\nimport aiohttp\n\nclass Client(revolt.Client):\n    async def on_message(self, message: revolt.Message):\n        if message.content == "hello":\n            await message.channel.send("hi how are you")\n\nasync def main():\n    async with aiohttp.ClientSession() as session:\n        client = Client(session, "BOT TOKEN HERE")\n        await client.start()\n\nasyncio.run(main())\n```\n',
    'author': 'Zomatee',
    'author_email': 'me@zomatree.live',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/revoltchat/revolt.py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
