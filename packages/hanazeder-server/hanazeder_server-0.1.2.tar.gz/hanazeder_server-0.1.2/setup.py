# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['hanazeder_server']

package_data = \
{'': ['*']}

install_requires = \
['asyncio-mqtt>=0.12.1,<0.13.0', 'hanazeder==1.2.0', 'quart>=0.18.0,<0.19.0']

setup_kwargs = {
    'name': 'hanazeder-server',
    'version': '0.1.2',
    'description': 'A server that reads energy and sensor data from a Hanazeder FP pump control system and publishes it to MQTT. Automatically creates Home Assistant topics.',
    'long_description': None,
    'author': 'Kevin Read',
    'author_email': 'me@kevin-read.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
