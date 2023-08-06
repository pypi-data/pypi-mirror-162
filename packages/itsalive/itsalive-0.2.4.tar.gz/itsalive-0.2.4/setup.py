# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['itsalive']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['itsalive = itsalive.cli:main']}

setup_kwargs = {
    'name': 'itsalive',
    'version': '0.2.4',
    'description': 'Autopilot for live demos.',
    'long_description': 'It\'s a Live\n===========\n\n![](misc/logo.png)\n\nIt\'s a Live is a utility that helps you make live coding demos less error-prone by taking the "live" component and\nkilling it.\n\nIt\'s a Live lets you write commands and keystrokes in a file, which it will then read and open a new terminal for you.\nEvery time you press a key, It\'s a Live will write one character from the file into the terminal, making it look like\nyou\'re typing every single command with the practiced ease of a consummate professional.\n\n\nWhat it looks like\n------------------\n\nThis is what it looks like:\n\n![](misc/screenshot.png)\n\nThe typing terminal is on the left and the presenter view is on the right.\n\nHere\'s a screencast of It\'s a Live in operation. Keep in mind that the presenter is pressing keys randomly after the\nprogram starts:\n\n[![asciicast](https://asciinema.org/a/308560.svg)](https://asciinema.org/a/308560)\n\n\nInstallation\n------------\n\nYou can install It\'s a Live with pip:\n\n```\npip install itsalive\n```\n\nThat\'s about it.\n\n\nUsage\n-----\n\nUsing It\'s a Live is pretty simple:\nJust write some keystrokes or commands in a file and run `itsalive` with it:\n\n```\nitsalive <command_file>\n```\n\nIt\'s a Live will wait for you to press a key, and, when you do, it will instead emit one character from the command\nfile. This way, you can type whatever old crap and it will look perfectly rehearsed, every time, with no backspaces\n(unless you add them in).  It will also wait for you to press Enter at the end of commands, so you will never skip\nahead to the next command by mistake.\n\nWhat\'s more, It\'s a Live is actually running the commands you\'re typing, so you have full interoperability with other\nprograms.\n\nIt\'s a Live also supports various commands:\n\n* `Ctrl+d` will immediately terminate the playback.\n* `Ctrl+p` will pause automatic playback and give you control of the terminal. This is useful for doing actually live\n  stuff, just make sure to leave everything in a state so that playback can resume later.\n* `Ctrl+r` will resume playback.\n* `Ctrl+f` will skip forward to the next command.\n* `Ctrl+g` will skip back to the previous command.\n* `Ctrl+u` will send a `Ctrl+u` keystroke (wiping anything on to the left of the cursor) and rewind the current command.\n* `Ctrl+e` will type out the current command in its entirety.\n\n\nPresenter view\n--------------\n\nIt\'s a Live supports a presenter view, which will show the next command to be typed. To launch the presenter view, start\nthe presentation and run, on a separate terminal:\n\n```\nitsalive presenter_view\n```\n\nIf you want to leave yourself notes, you can add comments to the command file. Comments must start with `##` as the\nfirst thing on the line, and they will not be typed. They will only be shown above the command in the presenter view.\n\n\nSpecial commands\n----------------\n\nThere are special commands you can add to your files. The line must start with them, with no spaces before them.\n\n---\n\n**`##@include <filename>`:** This inserts the contents of `<filename>` at the position of the `include` command. The\nfile will be typed out, as if you had pasted it in the commands file.\n\nExample: `##@include somefile.py`.\n\n**`##@pause`:** Pause automatic playback.  This is useful when you\'re executing a command and know that the command that follows will be manually interacted with.  This functionality is only available post command execution and is ignored when using skip key combinations (Ctrl+f / Ctrl+g).\n\n---\n\n\nLicense\n-------\n\nIt\'s a Live is licensed under the GPL v3 or any later version.\n\n\nAcknowledgements\n---------------\n\nI would like to thank my bestie Ian Cromwell, without whom this project would be nameless.\n\n# Changelog\n\n\n## v0.2.4 (2022-08-11)\n\n### Features\n\n* Feat: Add `##@pause` command. [James Spurin]\n\n* Colored presenter live updates. [James Spurin]\n\n### Fixes\n\n* Fix description. [Stavros Korokithakis]\n\n\n## v0.2.3 (2022-02-28)\n\n### Fixes\n\n* Don\'t eat characters when OSC codes are emitted. [James Spurin]\n\n\n## v0.2.2 (2021-09-30)\n\n### Features\n\n* Add "--clear" flag. [Stavros Korokithakis]\n\n### Fixes\n\n* Don\'t freeze in case a presentation packet is exactly as large as the buffer size. [Stavros Korokithakis]\n\n\n## v0.2.1 (2020-03-10)\n\n### Features\n\n* Add command gutter so empty lines are more obvious. [Stavros Korokithakis]\n\n### Fixes\n\n* Disallow jumping past the last command (and ending playback) [Stavros Korokithakis]\n\n* Don\'t skip over the last empty command. [Stavros Korokithakis]\n\n* Fix race condition where the socket thread printed things to the screen before curses was set up. [Stavros Korokithakis]\n\n* Add the missing `--address` argument. [Stavros Korokithakis]\n\n\n## v0.2.0 (2020-03-09)\n\n### Features\n\n* Add curses-based presenter view. [Stavros Korokithakis]\n\n* Add Ctrl+r as a resumption shortcut. [Stavros Korokithakis]\n\n### Fixes\n\n* Only update the presenter view if the command changes. [Stavros Korokithakis]\n\n* Change Ctrl+b to Ctrl+g, as the former clashed with tmux. [Stavros Korokithakis]\n\n\n## 0.1.3 (2020-03-04)\n\n### Features\n\n* Feat: Add `##@include` directive. [Stavros Korokithakis]\n\n\n',
    'author': 'Stavros Korokithakis',
    'author_email': 'hi@stavros.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/stavros/itsalive',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
