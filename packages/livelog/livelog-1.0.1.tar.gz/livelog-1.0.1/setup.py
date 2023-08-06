# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['livelog']

package_data = \
{'': ['*']}

install_requires = \
['colorama==0.4.5', 'watchdog==2.1.9']

setup_kwargs = {
    'name': 'livelog',
    'version': '1.0.1',
    'description': 'File logger and live reader',
    'long_description': '\n<div align="center">\n\n<h1>livelog</h1>\n\n<a href="https://img.shields.io/github/v/release/pablolec/livelog" target="_blank">\n    <img src="https://img.shields.io/github/v/release/pablolec/livelog" alt="Release">\n</a>\n\n<a href="https://github.com/PabloLec/livelog/blob/main/LICENSE" target="_blank">\n    <img src="https://img.shields.io/github/license/pablolec/livelog" alt="License">\n</a>\n\n<a href="https://github.com/PabloLec/livelog/actions/workflows/linux-tests.yml" target="_blank">\n    <img src="https://github.com/PabloLec/livelog/actions/workflows/linux-tests.yml/badge.svg" alt="Linux">\n</a>\n\n<a href="https://github.com/PabloLec/livelog/actions/workflows/macos-tests.yml" target="_blank">\n    <img src="https://github.com/PabloLec/livelog/actions/workflows/macos-tests.yml/badge.svg" alt="macOS">\n</a>\n\n<a href="https://github.com/PabloLec/livelog/actions/workflows/windows-tests.yml" target="_blank">\n    <img src="https://github.com/PabloLec/livelog/actions/workflows/windows-tests.yml/badge.svg" alt="Windows">\n</a>\n\n</div>\n\n---\n\n`livelog` is yet another Python logger.\n\nIts main purpose is to provide live logging for situation where logging to console is not possible. For example working on a GUI, TUI, a software plugin or a script instanciated from a different shell.\n\nIt provides a `Logger` object for your code and a built-in reader to see your logs in real time from another shell.\nEven if its overall behavior is opinionated it does offer some customization.\n\n## Demo\n\n<p align="center">\n    <img src="docs/assets/demo.gif">\n</p>\n\n\n## Installation\n\n```\npython3 -m pip install livelog\n```\n\n## Logging\n\n#### Basics\n\nIn your code, create a `Logger` instance with:\n\n``` python\nfrom livelog import Logger\n\nlogger = Logger()\n```\n\n#### Parameters\n\n`Logger` takes multiple optional arguments:\n\n- `file` (str): Path for your logging file. Default is a file named "livelog.log" in your system tmp directory.\n- `level` (str): Minimum level to be logged. Default is "DEBUG", you can also select "INFO", "WARNING", and "ERROR". Note that level filtering can also be done directly from the reader.\n- `enabled` (bool): Whether logging is enabled or not. Default is True.\n- `erase` (bool): Whether preexisting logging file should be erased or not. Default is True.\n\n``` python\nfrom livelog import Logger\n\nlogger = Logger(file= "/home/user/",\n                level = "INFO",\n                enabled = False,\n                erase = False)\n```\n\n#### Methods\n\nUse the following methods to write log messages:\n\n- `logger.debug("message")`\n- `logger.info("message")`\n- `logger.warn("message")`\n- `logger.error("message")`\n\n``` python\nfrom livelog import Logger\n\nlogger = Logger()\nlogger.debug("This is a debug message")\nlogger.info("This is an info message")\nlogger.warn("This is a warning message")\nlogger.error("This is an error message")\n```\n\n#### Attributes\n\nYou can get and set attributes after instantiation:\n\n``` python\nfrom livelog import Logger\n\nlogger = Logger(file="/tmp/file.log")\nlogger.debug("This will write to /tmp/file.log")\n\nlogger.file = "/tmp/another_file.log"\nlogger.debug("This will write to /tmp/another_file.log")\n\nlogger.level = "ERROR"\nlogger.debug("This debug message will not be written.")\n\nlogger.enabled = False\nlogger.error("Logging disabled. This error message will not be written.")\n```\n\n#### Singleton\n\n`livelog` also provides a built-in singleton:\n\n```your_first_file.py```\n``` python\nfrom livelog import LoggerSingleton\n\n\nlogger = LoggerSingleton(file="/tmp/file.log")\nlogger.debug("This will write to /tmp/file.log")\n```\n\n```another_file.py```\n``` python\nfrom livelog import LoggerSingleton\n\n\nlogger = LoggerSingleton()\n# LoggerSingleton() returned the instance from your first file.\nlogger.debug("This will write to /tmp/file.log")\n```\n\n## Reading\n\nAlthough you can access to your logging file like any other, you can use the provided reader.\n\nIf you did not specify a file for `Logger` simply use:\n```\npython3 -m livelog\n```\n\n`livelog` will read in real time the default log file.\n\n#### Options\n\n- `-f` or `--file` - Set the path of your logging file\n- `-l` or `--level` - Set the minimum log level to be read.\n- `--nocolors` - Do not print colors\n\n*Example:*\n```\npython3 -m livelog -f /tmp/myfile.log -l INFO --nocolors\n```\n',
    'author': 'PabloLec',
    'author_email': 'pablo.lecolinet@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/PabloLec/livelog',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
