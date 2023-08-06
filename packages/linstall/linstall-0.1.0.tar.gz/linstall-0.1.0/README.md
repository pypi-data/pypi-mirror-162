# linstall

A Python CLI to generate a list of installation commands for a package to add to README files.

## Development

- `poetry install`
- `poetry run linstall linstall Python` / `poetry run linstall --version` / `poetry run linstall --help`
- `poetry check`

## Notes

- Poetry:
  - [Install/Uninstall Poetry](https://python-poetry.org/docs/master/#installation)
  - `curl -sSL https://install.python-poetry.org | python3 - --preview`
  - `poetry --version`
  - `poetry config --list`
  - `poetry config virtualenvs.in-project true`
  - Dependencies:
    - Add the dependencies and just leave the version number in the `pyproject.toml` file for exact versions
    - `poetry add click markdown-subtemplate pyperclip`
    - `poetry add black isort flakeheaven flake8-use-fstring --group dev`
  - Delete the virtual environment: `poetry env remove python` ([source](https://github.com/python-poetry/poetry/issues/926#issuecomment-710056079))
- [Poetry Version Plugin](https://github.com/tiangolo/poetry-version-plugin):
  - `poetry self add poetry-version-plugin`
  - `poetry build`
  - `poetry self remove poetry-version-plugin`
  - [plugin does not work anymore with latest poetry 1.2.0b2](https://github.com/tiangolo/poetry-version-plugin/issues/25) (open) issue.
- [FlakeHeaven](https://github.com/flakeheaven/flakeheaven):
  - `poetry run flakeheaven missed`
  - `poetry run flakeheaven plugins`
  - `poetry run flakeheaven config` / `poetry run flakeheaven config --plugins-only`
  - `poetry run flakeheaven lint ./linstall/` / `poetry run flakeheaven lint --help`
  - By default, FlakeHeaven runs only `pyflakes` and `pycodestyle` ([source](https://flakeheaven.readthedocs.io/en/latest/config.html) and [source](https://flakeheaven.readthedocs.io/en/latest/plugins.html))
  - [IDE integration](https://flakeheaven.readthedocs.io/en/latest/ide.html) documentation
  - [IDE Integration fails on VSCode](https://github.com/flakeheaven/flakeheaven/issues/32) (open) issue and [BUG: flake8heavened just runs flake8 in VSCode](https://github.com/flakeheaven/flakeheaven/issues/127) issue
  - `poetry run flakeheaven code FS001` ([source](https://flakeheaven.readthedocs.io/en/latest/commands/code.html))
  - `poetry run flakeheaven codes flake8-use-fstring` ([source](https://flakeheaven.readthedocs.io/en/latest/commands/codes.html))
- Commands:
  - Python:
    - [pip](https://pip.pypa.io/en/stable/cli/pip_install/): `pip install`
    - [Pipenv](https://pipenv.pypa.io/en/latest/install/#installing-packages-for-your-project): `pipenv install`
    - [Poetry](https://python-poetry.org/docs/master/cli/#add): `poetry add`
    - [PDM](https://python-poetry.org/docs/master/cli/#add) ([example](https://github.com/pdm-project/pdm#quickstart)): `pdm add`
    - [Pyflow](https://github.com/David-OConnor/pyflow#what-you-can-do): `pyflow install`
- [shellingham](https://github.com/sarugaku/shellingham)
