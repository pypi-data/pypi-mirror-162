# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tor_python_easy']

package_data = \
{'': ['*']}

install_requires = \
['requests>=2.26.0,<3.0.0']

setup_kwargs = {
    'name': 'tor-python-easy',
    'version': '0.1.3',
    'description': 'Simple library to manage tor proxy and IP changes',
    'long_description': "# tor-python-easy\n\n**tor-python-easy** was developed for use tor proxy in python with easy interface, which allow for\nchanging ip address whenever you want.\n\nRepo is very simple but if you want you can **add new feature request**.\n\n## Donate\n\nIf you want to sponsor me, in thanks for the project, please send me some crypto 😁:\n\n|Coin|Wallet address|\n|---|---|\n|Bitcoin|`3EajE9DbLvEmBHLRzjDfG86LyZB4jzsZyg`|\n|Etherum|`0xE43d8C2c7a9af286bc2fc0568e2812151AF9b1FD`|\n\n## Installation\n\nLibrary is only one file, so you can copy it to project.\n\nHowever, if you want you can install it with pip:\n\n```bash\npip3 install tor-python-easy\n```\n\n## Run tor proxy\n\nThere are two simple ways to run tor proxy.\n\n1. First one is using docker and docker-compose from this repo. You can manipulate with mapping\n   ports and password.\n   ```shell\n   docker-compose up\n   ```\n2. Second one uses tor installed in OS\n   ```shell\n   tor --controlport 9051 \n   ```\n\n## Use lib with python\n\n1. In terminal\n   ```shell\n   docker-compose up\n   ```\n2. In Python\n   ```python\n   from tor_python_easy.tor_control_port_client import TorControlPortClient\n   from tor_python_easy.tor_socks_get_ip_client import TorSocksGetIpClient\n   \n   if __name__ == '__main__':\n       proxy_config = {\n           'http': 'socks5://localhost:9050',\n           'https': 'socks5://localhost:9050',\n       }\n       ip_client = TorSocksGetIpClient(proxy_config)\n       tor_control_port_client = TorControlPortClient('localhost', 9051, 'test1234')\n   \n       for it in range(10):\n           old_ip = ip_client.get_ip()\n           tor_control_port_client.change_connection_ip(seconds_wait=10)\n           new_ip = ip_client.get_ip()\n           print(f'iteration {it + 1} ::  {old_ip} -> {new_ip}')\n   ```\n   \n   Output will give 10 IP migrations.\n",
    'author': 'Marcin Wątroba',
    'author_email': 'markowanga@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/markowanga/tor-python-easy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
