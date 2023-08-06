# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_bawiki']

package_data = \
{'': ['*'], 'nonebot_plugin_bawiki': ['res/*']}

install_requires = \
['Jinja2>=3.1.2,<4.0.0',
 'aiohttp>=3.8.1,<4.0.0',
 'nonebot-adapter-onebot>=2.1.1,<3.0.0',
 'nonebot-plugin-htmlrender>=0.1.1,<0.2.0',
 'nonebot2>=2.0.0-beta.5,<3.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-bawiki',
    'version': '0.2.0',
    'description': 'A nonebot2 plugin for Blue Archive.',
    'long_description': '<!-- markdownlint-disable MD033 MD036 MD041 -->\n\n<div align="center">\n  <a href="https://v2.nonebot.dev/store"><img src="readme/nonebot-plugin-bawiki.png" width="200" height="200" alt="BAWiki"></a>\n</div>\n\n<div align="center">\n\n# NoneBot-Plugin-BAWiki\n\n_✨ 基于 NoneBot2 的碧蓝档案 Wiki 插件 ✨_\n\n<a href="./LICENSE">\n    <img src="https://img.shields.io/github/license/lgc2333/nonebot-plugin-bawiki.svg" alt="license">\n</a>\n<a href="https://pypi.python.org/pypi/nonebot-plugin-bawiki">\n    <img src="https://img.shields.io/pypi/v/nonebot-plugin-bawiki.svg" alt="pypi">\n</a>\n<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">\n<a href="https://pypi.python.org/pypi/nonebot-plugin-bawiki">\n    <img src="https://img.shields.io/pypi/dm/nonebot-plugin-bawiki" alt="pypi download">\n</a>\n\n</div>\n\n## 📖 介绍\n\n一个碧蓝档案的 Wiki 插件，目前写了活动日程和学生图鉴，数据来源为 [GameKee](https://ba.gamekee.com/)\n\n## 💿 安装\n\n<details open>\n<summary>【推荐】使用 nb-cli 安装</summary>\n在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装\n\n    nb plugin install nonebot-plugin-bawiki\n\n</details>\n\n<details>\n<summary>使用包管理器安装</summary>\n在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令\n\n<details>\n<summary>pip</summary>\n\n    pip install nonebot-plugin-bawiki\n\n</details>\n<details>\n<summary>pdm</summary>\n\n    pdm add nonebot-plugin-bawiki\n\n</details>\n<details>\n<summary>poetry</summary>\n\n    poetry add nonebot-plugin-bawiki\n\n</details>\n<details>\n<summary>conda</summary>\n\n    conda install nonebot-plugin-bawiki\n\n</details>\n\n打开 nonebot2 项目的 `bot.py` 文件, 在其中写入\n\n    nonebot.load_plugin(\'nonebot_plugin_bawiki\')\n\n</details>\n\n<details>\n<summary>从 github 安装</summary>\n在 nonebot2 项目的插件目录下, 打开命令行, 输入以下命令克隆此储存库\n\n    git clone https://github.com/lgc2333/nonebot-plugin-bawiki.git\n\n打开 nonebot2 项目的 `bot.py` 文件, 在其中写入\n\n    nonebot.load_plugin(\'src.plugins.nonebot_plugin_bawiki\')\n\n</details>\n\n## ⚙️ 配置\n\n暂无配置\n\n<!--\n在 nonebot2 项目的`.env`文件中添加下表中的必填配置\n\n| 配置项 | 必填 | 默认值 | 说明 |\n|:-----:|:----:|:----:|:----:|\n| 配置项1 | 是 | 无 | 配置说明 |\n| 配置项2 | 否 | 无 | 配置说明 |\n-->\n\n## 🎉 使用\n\n### 指令表\n\n|     指令     | 权限 | 需要@ | 范围 |                     说明                      |\n| :----------: | :--: | :---: | :--: | :-------------------------------------------: |\n|  `ba日程表`  |  无  |  否   | 均可 |                      无                       |\n| `ba学生图鉴` |  无  |  否   | 均可 | 需要在后面加上学生名字，比如`ba学生图鉴 白子` |\n\n待更新\n\n### 效果图\n\n<details>\n<summary>长图，点击展开</summary>\n\n![example](readme/example.png)\n\n</details>\n\n## 📞 联系\n\nQQ：3076823485  \nTelegram：[@lgc2333](https://t.me/lgc2333)  \n吹水群：[1105946125](https://jq.qq.com/?_wv=1027&k=Z3n1MpEp)  \n邮箱：<lgc2333@126.com>\n\n## 💡 鸣谢\n\n### [RainNight0](https://github.com/RainNight0)\n\n- 日程表 html 模板提供\n\n## 💰 赞助\n\n感谢大家的赞助！你们的赞助将是我继续创作的动力！\n\n- [爱发电](https://afdian.net/@lgc2333)\n- <details>\n    <summary>赞助二维码（点击展开）</summary>\n\n  ![讨饭](https://raw.githubusercontents.com/lgc2333/ShigureBotMenu/master/src/imgs/sponsor.png)\n\n  </details>\n\n## 📝 更新日志\n\n### 0.1.1\n\n- 日程表改为以图片形式发送\n- 日程表不会显示未开始的活动了\n- 小 bug 修复\n- ~~移除了 herobrine~~\n',
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
