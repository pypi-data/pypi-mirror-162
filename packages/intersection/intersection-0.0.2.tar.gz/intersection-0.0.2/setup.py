# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['intersection']

package_data = \
{'': ['*']}

install_requires = \
['Unidecode>=1.3.4,<2.0.0',
 'click>=8.1.3,<9.0.0',
 'nanoid>=2.0.0,<3.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'python-telegram-bot>=13.13,<14.0']

entry_points = \
{'console_scripts': ['intersection-game = intersection.cli:start']}

setup_kwargs = {
    'name': 'intersection',
    'version': '0.0.2',
    'description': 'Telegram based version of a text based game where two players try to find the same word.',
    'long_description': "# Intersection\n\n[Telegram](https://telegram.org/) based version of a text based game where two players try to find the same word.\n\n## Start\n\n👋 Hello and welcome to The Intersection Game!  \nThis is a two-player game so you must find another player to start a game.  \nTo do so you must use the /play command. Typing /play will put you inside a game; if another player also uses /play soon after you, the game will start with this person as the other player.  \nIf you specify a password (e.g. `/play 123`) you will only play against a player who uses the same password.  \nOn each round, each player must enter their word. The goal is to enter the same word based on the two previously entered ones. Words may only be used once per game.  \nHave fun!\n\n## Help\n\nHere is the list of what you can do:  \n/start - Displays the start message and the rules.  \n/help - Displays a description of available commands.  \n/play [password] - Starts a new game with the optional password. Places you in the waiting room if no password is provided.  \n/stop - Terminates your current game.  \nSimply send me your next word when within a game (won't take accents and capitals into account).\n\n## Run instance\n\n1. Install using `pip install intersection`\n2. Specify the environnement variable `INTERSECTION_TELEGRAM_BOT_TOKEN` (see [How to create a Telegram bot](https://core.telegram.org/bots#3-how-do-i-create-a-bot))\n3. Start the bot using the `intersection-game` command\n",
    'author': 'gruvw',
    'author_email': 'gruvw.dev@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gruvw/intersection',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
