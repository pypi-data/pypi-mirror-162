# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['novabot_plugin_word_bank']

package_data = \
{'': ['*']}

install_requires = \
['aiofiles>=0.8.0,<0.9.0', 'httpx>=0.23.0,<0.24.0']

setup_kwargs = {
    'name': 'novabot-plugin-word-bank',
    'version': '0.1.0',
    'description': 'Nova-Bot 使用的无数据库的问答插件',
    'long_description': None,
    'author': 'NovaNo1r',
    'author_email': 'mail@novanoir.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
