# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['please']

package_data = \
{'': ['*']}

install_requires = \
['rich>=12.3.0,<13.0.0', 'typer>=0.4.1,<0.5.0']

entry_points = \
{'console_scripts': ['please = please.please:main']}

setup_kwargs = {
    'name': 'please-cli',
    'version': '0.3.0',
    'description': 'A new tab page for your terminal',
    'long_description': '<h1 align="center">🙏 Please - New Tab Page for your Terminal 🙏</h1>\n\n<h4 align="center">Get a beautifully formatted minimalistic new tab page with a greeting, date and time, inspirational quotes, your personal tasks and to-do list everytime you open the terminal with Please CLI.</h4>\n\n<p align="center"><img src="https://user-images.githubusercontent.com/25067102/173348894-09190c99-baff-477a-9b48-b4d3cff0f029.gif"></img></center>\n\n# [New version out now!](https://github.com/NayamAmarshe/please/releases/tag/0.2.0)\n### Upgrade with `pip3 install please-cli --upgrade`\n\n# 📖 Table of Contents\n\n- [🚀 Installation](#-installation)\n   - [1️⃣ Method 1](#method-1)\n   - [2️⃣ Method 2](#method-2)\n- [🚑 Troubleshooting](#-troubleshooting)\n- [👨\u200d💻 Commands](#-commands)\n- [🧰 Additional Optional Configuration](#-additional-optional-configuration)\n- [🚮 Uninstalling](#-uninstalling)\n- [❤ Credits](#-credits)\n\n# 🚀 Installation\n\n### Method 1:\n\n1. Make sure you have Python 3 installed on your computer.\n2. Open your terminal and paste the command below:\n\n   ```bash\n   pip install please-cli\n\n   # If you get an error about \'pip not found\', just replace pip with pip3.\n   ```\n\n3. To run **please** everytime you open the terminal:\n\n   ```bash\n   # FOR BASH\n   echo \'please\' >> ~/.bashrc\n\n   # FOR ZSH\n   echo \'please\' >> ~/.zshrc\n   ```\n\n4. That\'s it! Check if `please` command works in your terminal.\n\n### Method 2:\n\n1. Go to the releases section.\n2. Download the latest release WHL file.\n3. Open terminal and paste the command below:\n\n   ```bash\n   pip install --user ~/Downloads/please_cli*\n\n   # If you get an error about \'pip not found\', just replace pip with pip3.\n   ```\n\n   Change the path of the file if you downloaded it elsewhere.\n\n4. To run **please** everytime you open the terminal:\n\n   ```bash\n   # FOR BASH\n   echo \'please\' >> ~/.bashrc\n\n   # FOR ZSH\n   echo \'please\' >> ~/.zshrc\n   ```\n\n5. That\'s it! Check if `please` command works in your terminal.\n\n###### Having trouble with installation or have any ideas? Please create an issue ticket :)\n\n# 🚑 Troubleshooting\n\nGetting a `command not found: please` error? That means the Python modules installation folder is not in PATH.\nTo fix this:\n\n```bash\necho \'export PATH="$PATH:$HOME/.local/bin"\' >> ~/.profile\n```\n\n# 👨\u200d💻 Commands\n\n```bash\n# Show time, quotes and tasks\nplease\n\n# Add a task\nplease add "TASK NAME"\n\n# Delete a task\nplease delete <TASK NUMBER>\n\n# Mark task as done\nplease do <TASK NUMBER>\n\n# Mark task as undone\nplease undo <TASK NUMBER>\n\n# Show tasks even if all tasks are markded as done\nplease showtasks\n\n# Move task to specified position\nplease move <OLD NUMBER> <NEW NUMBER>\n\n# Toggle Time between 24 hours and 12 hours format\nplease changetimeformat\n\n# Change your name\nplease callme "NAME"\n\n# Delete all done tasks\nplease clean\n\n# Reset all settings and tasks\nplease setup\n```\n\n# 🧰 Additional Optional Configuration\n\n## Remove Horizontal Line in please\'s output\n\n1.Navigate to `~/.config/please`  \n2. Open config.json  \n3. Add `"diable_line": true` at the end (don\'t forget to add a `,` at the end of the previous line)\\\n![](./illustration1.jpg)\n\n# 💻 Local Development\n\n1. To get started, first install poetry:\n\n```bash\ncurl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -\n```\n\n2. Clone this project\n3. `cd` to the project directory and run virtual environment:\n\n```bash\npoetry shell\n\n# OR THIS, IF \'poetry shell\' doesn\'t work\n\n. "$(dirname $(poetry run which python))/activate"\n```\n\n4. Install all dependencies:\n\n```bash\npoetry install\n```\n\n- `please` will be available to use as a command in the virtual environment after using `poetry install`.\n\n5. Finally, run the python script with:\n\n```bash\npython please/please.py\n```\n\n6. To build a WHL package:\n\n```bash\npoetry build\n```\n\n- The package will be generated in **dist** folder, you can then use pip to install the WHL file.\n\n# 🚮 Uninstalling\n\nOpen your terminal and type:\n\n```bash\npip uninstall please-cli\n```\n\nand also edit your **.zshrc** or **.bashrc** file and remove the line that says `please` at the end of the file.\n\n# ♥ Credits\n\n- Thanks to @CodePleaseRun & @guedesfelipe for their contributions.\n- Thanks to @lukePeavey for the quotes.json file taken from quotable.io\n\n#\n\n<h4 align="center"> Made by TGS963 and NayamAmarshe with ⌨ and 🖱 </h4>\n',
    'author': 'Nayam Amarshe',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/NayamAmarshe/please',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
