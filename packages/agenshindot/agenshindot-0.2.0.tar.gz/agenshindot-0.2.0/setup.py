# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['agenshindot',
 'agenshindot.database',
 'agenshindot.database.action',
 'agenshindot.database.model',
 'agenshindot.modules',
 'agenshindot.modules.mihoyo_bbs',
 'agenshindot.modules.wiki',
 'agenshindot.utils',
 'agenshindot.utils.mihoyo_bbs',
 'agenshindot.utils.mihoyo_bbs.model',
 'agenshindot.utils.minigg',
 'agenshindot.utils.minigg.model']

package_data = \
{'': ['*'], 'agenshindot': ['resource/mihoyo_bbs/*']}

install_requires = \
['Pillow>=9.2.0,<10.0.0',
 'SQLAlchemy>=1.4.39,<2.0.0',
 'aiosqlite>=0.17.0,<0.18.0',
 'graia-ariadne[standard]>=0.8.1,<0.9.0',
 'prompt-toolkit>=3.0.30,<4.0.0',
 'tomlkit>=0.11.2,<0.12.0']

setup_kwargs = {
    'name': 'agenshindot',
    'version': '0.2.0',
    'description': 'GenshinDot for Python, powered by Graia-Ariadne.',
    'long_description': '# AGenshinDot\n\n[![PyPI](https://img.shields.io/pypi/v/agenshindot?style=flat-square)](https://pypi.org/project/agenshindot)\n[![Python Version](https://img.shields.io/pypi/pyversions/agenshindot?style=flat-square)](https://pypi.org/project/agenshindot)\n[![License](https://img.shields.io/github/license/MingxuanGame/AGenshinDot?style=flat-square)](https://github.com/MingxuanGame/AGenshinDot/blob/master/LICENSE)\n[![QQ群](https://img.shields.io/badge/QQ%E7%BE%A4-929275476-success?style=flat-square)](https://jq.qq.com/?_wv=1027&k=C7XY04F1)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?&labelColor=ef8336)](https://pycqa.github.io/isort/)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/MingxuanGame/AGenshinDot/master.svg)](https://results.pre-commit.ci/latest/github/MingxuanGame/AGenshinDot/master)\n\nAGenshinDot 是 [GenshinDot](https://github.com/MingxuanGame/GenshinDot) 的 Python 实现，由 [Graia-Ariadne](https://github.com/GraiaProject/Ariadne) 驱动.\n\n## 声明\n\nAGenshinDot 遵循 `AGPLv3` 许可协议开放全部源代码，你可在[这里](./LICENSE)找到本项目的许可证.\n\nAGenshinDot 仅供学习娱乐使用，禁止将此 Bot 用于商用和非法用途.\n\nAGenshinDot 项目及作者不对因使用本项目所造成的损失进行赔偿，也不承担任何法律责任.\n\n## 安装\n\n### 从 PyPI 安装\n\n```bash\npip install agenshindot\n# or\npoetry add agenshindot\n```\n\n### 从 GitHub 安装\n\n1.直接安装\n\n```bash\npoetry add git+https://github.com/MingxuanGame/AGenshinDot.git\n```\n\n2.克隆后安装\n\n```bash\ngit clone https://github.com/MingxuanGame/AGenshinDot.git\ncd AGenshinDot\npoetry install --no-dev\n```\n\n## 配置\n\n所有配置均保存在运行目录 `config.toml`.\n\n下面为配置样例：\n\n```toml\n# 机器人 QQ 号\naccount = 1185285105\n# verifyKey\nverify_key = "agenshindot"\n# 是否启用控制台\nenable_console = false\n# 是否开启 Cookie 绑定\nenable_bind_cookie = false\n# 机器人管理员 QQ 号\nadmins = [1060148379]\n\n# 以下为连接配置\n# 如果不配置则默认为 HTTP + 正向 WebSocket，连接地址为 localhost:8080\n# 可以同时配置多种连接\n\n# 正向 WebSocket 配置\nws = "ws://localhost:8080"\n# 等同于如下配置\n# ws = ["ws://localhost:8080"]\n\n# HTTP 配置\nhttp = "http://localhost:8080"\n# 等同于如下配置\n# http = ["http://localhost:8080"]\n\n# 反向 WebSocket 配置\n[ws_reverse]\n# Endpoint\npath = "/"\n# 验证的参数\nparams = {}\n# 验证的请求头\nheaders = {}\n# WARNING 上面的配置要保证不能缺失，也不能调换位置\n# 如果只需要设置 Endpoint，也可以使用下方的配置\n# ws_reverse = "/"\n\n# HTTP Webhook 配置\n[webhook]\n# Endpoint\npath = "/"\n# 验证的请求头\nheaders = {}\n# WARNING 上面的配置要保证不能缺失，也不能调换位置\n# 如果只需要设置 Endpoint，也可以使用下方的配置\n# webhook = "/"\n\n# 日志配置\n[log]\n# 日志等级，详情请看 loguru 文档\nlevel = "INFO"\n# 过期时间，过期的日志将被删除，格式请看 \n# https://pydantic-docs.helpmanual.io/usage/types/#datetime-types\n# 中 `timedelta` 部分\nexpire_time = "P14DT0H0M0S"\n# 是否启用数据库日志\ndb_log = false\n```\n\n## 启动\n\n1.执行本项目文件夹下的 `bot.py`\n\n```bash\npython bot.py\n```\n\n2.以模块形式启动\n\n```bash\npython -m agenshindot\n```\n\n## 控制台命令\n\n> WARNING\n> 控制台属于实验性内容，不建议使用\n>\n>启用控制台后，会禁用标准输出中 **日志等级** 的设置\n\n在启用控制台后，可以输入以下命令执行一些操作\n\n* `/stop`\n\n  关闭 AGenshinDot.\n\n* `/license`\n\n  输出许可证信息.\n\n* `/version`\n\n  输出 AGenshinDot LOGO 和版本信息.\n\n* `/execute <SQL 语句>`\n\n  执行 SQL 语句 **（危险操作）**\n',
    'author': 'MingxuanGame',
    'author_email': 'MingxuanGame@outlook.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MingxuanGame/AGenshinDot',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
