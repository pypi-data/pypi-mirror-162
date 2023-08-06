# Stackler

Working with Phabricator Stack has never been so easy.

```
$ stackler submit -m "rebase msg"
By continuing, this script will:
Update D157389 with [24a42cd9 1/3 Add Framework], message: rebase msg.
Update D157390 with [67cfa09f 2/3 Add UI], message: rebase msg.
Submit [7bc9760d 3/3 Add API] based on [67cfa09f 2/3 Add the UI framework fo...].
```

* Submit/Update all the commits into a Phabricator Stack
* (WIP) Land the entire stack one by one
* (WIP) After `git checkout <SHA>`, easily restore the commit tree

# Install

## TL;DR
```
# install from pip
pip3 install --user stackler
```

## Add to PATH
If your path isn't setup to work with pip already, as in if you see 
> "WARNING: The script stackler is installed in <pip-path> which is not on PATH."

You need to add the pip executable path to your `$PATH`. Here are some examples:

* bash
  
  ```
  echo -n 'PATH="$(python3 -m site --user-base)/bin:${PATH}"' >> ~/.bash_profile
  ```

* zsh
  
  ```
  echo -n 'PATH="$(python3 -m site --user-base)/bin:${PATH}"' >> ~/.zshrc
  ```

# Develop

## Setup Enviornment
```
poetry install
poetry config virtualenvs.in-project true
poetry shell
```
 Make sure you use the Python in the virtual environment setup by `poetry`. In
 VS Code, use ⌘⇧P and enter Select Interpreter, then pick the one with python.

## Linter and Formatter

As specified in the [VS Code setting file
(`.vscode/settings.json`)](.vscode/settings.json), this project uses
[pylint](https://pypi.org/project/pylint/) for linting and
[autopep8](https://pypi.org/project/autopep8/) for auto formatting.


# Publish

> This is mostly an excerpt from [Typer CLI's publish documentataion](https://typer.tiangolo.com/tutorial/package/).

## Add PyPI API Token (Once)
* Gain access to the PyPI project.
* Generate a token from https://pypi.org/manage/account/token/.
* Add the token to poetry.
```
poetry config pypi-token.pypi <pypi api token>
```

## Publish to PyPI
* Make sure you bump the version.
* Publish.
```
poetry publish --build
```