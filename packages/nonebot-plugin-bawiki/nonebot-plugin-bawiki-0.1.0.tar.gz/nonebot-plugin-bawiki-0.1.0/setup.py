# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_bawiki']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'nonebot-adapter-onebot>=2.1.1,<3.0.0',
 'nonebot-plugin-htmlrender>=0.1.1,<0.2.0',
 'nonebot2>=2.0.0-beta.5,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-bawiki',
    'version': '0.1.0',
    'description': 'A nonebot2 plugin for Blue Archive.',
    'long_description': None,
    'author': 'student_2333',
    'author_email': 'lgc2333@126.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
