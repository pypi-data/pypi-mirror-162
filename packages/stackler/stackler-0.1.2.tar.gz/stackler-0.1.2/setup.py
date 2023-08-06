# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stackler']

package_data = \
{'': ['*']}

install_requires = \
['GitPython==3.1.27',
 'click==8.1.3',
 'phabricator==0.9.1',
 'termcolor==1.1.0',
 'typer==0.6.1']

entry_points = \
{'console_scripts': ['stackler = stackler.main:app']}

setup_kwargs = {
    'name': 'stackler',
    'version': '0.1.2',
    'description': '',
    'long_description': '# Stackler\n\nWorking with Phabricator Stack has never been so easy.\n\n```\n$ stackler submit -m "rebase msg"\nBy continuing, this script will:\nUpdate D157389 with [24a42cd9 1/3 Add Framework], message: rebase msg.\nUpdate D157390 with [67cfa09f 2/3 Add UI], message: rebase msg.\nSubmit [7bc9760d 3/3 Add API] based on [67cfa09f 2/3 Add the UI framework fo...].\n```\n\n* Submit/Update all the commits into a Phabricator Stack\n* (WIP) Land the entire stack one by one\n* (WIP) After `git checkout <SHA>`, easily restore the commit tree\n\n# Install\n\n## TL;DR\n```\n# install from pip\npip3 install --user stackler\n```\n\n## Add to PATH\nIf your path isn\'t setup to work with pip already, as in if you see \n> "WARNING: The script stackler is installed in <pip-path> which is not on PATH."\n\nYou need to add the pip executable path to your `$PATH`. Here are some examples:\n\n* bash\n  \n  ```\n  echo -n \'PATH="$(python3 -m site --user-base)/bin:${PATH}"\' >> ~/.bash_profile\n  ```\n\n* zsh\n  \n  ```\n  echo -n \'PATH="$(python3 -m site --user-base)/bin:${PATH}"\' >> ~/.zshrc\n  ```\n\n# Develop\n\n## Setup Enviornment\n```\npoetry install\npoetry config virtualenvs.in-project true\npoetry shell\n```\n Make sure you use the Python in the virtual environment setup by `poetry`. In\n VS Code, use ⌘⇧P and enter Select Interpreter, then pick the one with python.\n\n## Linter and Formatter\n\nAs specified in the [VS Code setting file\n(`.vscode/settings.json`)](.vscode/settings.json), this project uses\n[pylint](https://pypi.org/project/pylint/) for linting and\n[autopep8](https://pypi.org/project/autopep8/) for auto formatting.\n\n\n# Publish\n\n> This is mostly an excerpt from [Typer CLI\'s publish documentataion](https://typer.tiangolo.com/tutorial/package/).\n\n## Add PyPI API Token (Once)\n* Gain access to the PyPI project.\n* Generate a token from https://pypi.org/manage/account/token/.\n* Add the token to poetry.\n```\npoetry config pypi-token.pypi <pypi api token>\n```\n\n## Publish to PyPI\n* Make sure you bump the version.\n* Publish.\n```\npoetry publish --build\n```',
    'author': 'Modun',
    'author_email': 'modun@xiaohongshu.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
