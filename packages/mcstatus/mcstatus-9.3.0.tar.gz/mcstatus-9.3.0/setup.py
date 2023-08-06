# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'mcstatus'}

packages = \
['mcstatus',
 'mcstatus.protocol',
 'mcstatus.tests',
 'mcstatus.tests.protocol',
 'protocol']

package_data = \
{'': ['*']}

install_requires = \
['asyncio-dgram==2.1.2', 'click>=7.1.2,<9', 'dnspython==2.2.1']

entry_points = \
{'console_scripts': ['mcstatus = mcstatus.__main__:cli']}

setup_kwargs = {
    'name': 'mcstatus',
    'version': '9.3.0',
    'description': 'A library to query Minecraft Servers for their status and capabilities.',
    'long_description': '# <img src="https://i.imgur.com/nPCcxts.png" height=25> MCStatus\n[![discord chat](https://img.shields.io/discord/936788458939224094.svg?logo=Discord)](https://discord.gg/C2wX7zduxC)\n![supported python versions](https://img.shields.io/pypi/pyversions/mcstatus.svg)\n[![current PyPI version](https://img.shields.io/pypi/v/mcstatus.svg)](https://pypi.org/project/mcstatus/)\n[![Validation](https://github.com/py-mine/mcstatus/actions/workflows/validation.yml/badge.svg)](https://github.com/py-mine/mcstatus/actions/workflows/validation.yml)\n[![Tox test](https://github.com/py-mine/mcstatus/actions/workflows/tox-test.yml/badge.svg)](https://github.com/py-mine/mcstatus/actions/workflows/tox-test.yml)\n\nMcstatus provides an easy way to query Minecraft servers for any information they can expose.  \nIt includes three modes of access (`query`, `status` and `ping`), the differences of which are listed below in usage.\n\n## Usage\n\nWe provide both an API which you can use in your projects, and a command line script, to quickly query a server.\n\n### Python API\n\nJava Edition\n```python\nfrom mcstatus import JavaServer\n\n# You can pass the same address you\'d enter into the address field in minecraft into the \'lookup\' function\n# If you know the host and port, you may skip this and use JavaServer("example.org", 1234)\nserver = JavaServer.lookup("example.org:1234")\n\n# \'status\' is supported by all Minecraft servers that are version 1.7 or higher.\nstatus = server.status()\nprint(f"The server has {status.players.online} players and replied in {status.latency} ms")\n\n# \'ping\' is supported by all Minecraft servers that are version 1.7 or higher.\n# It is included in a \'status\' call, but is also exposed separate if you do not require the additional info.\nlatency = server.ping()\nprint(f"The server replied in {latency} ms")\n\n# \'query\' has to be enabled in a servers\' server.properties file!\n# It may give more information than a ping, such as a full player list or mod information.\nquery = server.query()\nprint(f"The server has the following players online: {\', \'.join(query.players.names)}")\n```\n\nBedrock Edition\n```python\nfrom mcstatus import BedrockServer\n\n# You can pass the same address you\'d enter into the address field in minecraft into the \'lookup\' function\n# If you know the host and port, you may skip this and use MinecraftBedrockServer("example.org", 19132)\nserver = BedrockServer.lookup("example.org:19132")\n\n# \'status\' is the only feature that is supported by Bedrock at this time.\n# In this case status includes players_online, latency, motd, map, gamemode, and players_max. (ex: status.gamemode)\nstatus = server.status()\nprint(f"The server has {status.players_online} players online and replied in {status.latency} ms")\n```\n\n### Command Line Interface\n\nAt present time, this only works with Java servers, Bedrock is not yet supported.\n```\n$ mcstatus\nUsage: mcstatus [OPTIONS] ADDRESS COMMAND [ARGS]...\n\n  mcstatus provides an easy way to query Minecraft servers for any\n  information they can expose. It provides three modes of access: query,\n  status, and ping.\n\n  Examples:\n\n  $ mcstatus example.org ping\n  21.120ms\n\n  $ mcstatus example.org:1234 ping\n  159.903ms\n\n  $ mcstatus example.org status\n  version: v1.8.8 (protocol 47)\n  description: "A Minecraft Server"\n  players: 1/20 [\'Dinnerbone (61699b2e-d327-4a01-9f1e-0ea8c3f06bc6)\']\n\n  $ mcstatus example.org query\n  host: 93.148.216.34:25565\n  software: v1.8.8 vanilla\n  plugins: []\n  motd: "A Minecraft Server"\n  players: 1/20 [\'Dinnerbone (61699b2e-d327-4a01-9f1e-0ea8c3f06bc6)\']\n\nOptions:\n  -h, --help  Show this message and exit.\n\nCommands:\n  json    combination of several other commands with json formatting\n  ping    prints server latency\n  query   detailed server information\n  status  basic server information\n```\n\n## Installation\n\nMcstatus is available on [PyPI](https://pypi.org/project/mcstatus/), and can be installed trivially with:\n\n```bash\npython3 -m pip install mcstatus\n```\n\nAlternatively, just clone this repo!\n\n## License\n\nMcstatus is licensed under the Apache 2.0 license.\n',
    'author': 'Nathan Adams',
    'author_email': 'dinnerbone@dinnerbone.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/py-mine/mcstatus',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4',
}


setup(**setup_kwargs)
