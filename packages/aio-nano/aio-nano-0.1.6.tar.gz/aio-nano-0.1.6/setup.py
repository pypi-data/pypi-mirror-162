# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aio_nano', 'aio_nano.rpc', 'aio_nano.ws']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0', 'pydantic>=1.9.1,<2.0.0', 'websockets>=10.3,<11.0']

setup_kwargs = {
    'name': 'aio-nano',
    'version': '0.1.6',
    'description': 'An asynchronous nano currency library',
    'long_description': '# aio-nano\n\n## Overview\n\nThis library contains an asynchronous python RPC client for Nano nodes, allowing you to more easily develop on the Nano network with with fully type annnotated methods and responses.\n\n## Installation\n\n### PIP\n\n`pip install aio-nano`\n\n### Poetry\n\n`poetry add aio-nano`\n\n## Example Async HTTP RPC Call\n\n```python\nfrom aio_nano import Client\nimport asyncio\n\nasync def main():\n  api_key = ...\n  client = Client(\'https://mynano.ninja/api/node\', {\'Authorization\': api_key})\n\n  supply = await client.available_supply()\n  print(supply)\n\nasyncio.run(main())\n```\n\n## Example Async WebSocket RPC Subscription\n\n```python\nimport asyncio\nfrom time import time\n\nfrom aio_nano import WSClient\n\n\nasync def main():\n  ws = await WSClient("ws://localhost:7078").connect()\n  start = time() * 1000\n  await ws.subscribe("confirmation", lambda x: print(x), ack=True)\n  print(f"Acked in {time() * 1000 - start}ms")\n\n  await asyncio.Future()\n\n\nasyncio.run(main())\n\n```\n',
    'author': 'Teslim Olunlade',
    'author_email': 'tolunlade@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ogtega/aio-nano',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
