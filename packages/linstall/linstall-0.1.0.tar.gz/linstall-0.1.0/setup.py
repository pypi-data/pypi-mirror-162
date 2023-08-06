# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['linstall', 'linstall.templates']

package_data = \
{'': ['*']}

install_requires = \
['click==8.1.3', 'markdown-subtemplate==0.2.22', 'pyperclip==1.8.2']

entry_points = \
{'console_scripts': ['linstall = linstall.console:run']}

setup_kwargs = {
    'name': 'linstall',
    'version': '0.1.0',
    'description': 'A Python CLI to generate a list of installation commands for a package to add to README files.',
    'long_description': '# linstall\n\nA Python CLI to generate a list of installation commands for a package to add to README files.\n\n## Development\n\n- `poetry install`\n- `poetry run linstall linstall Python` / `poetry run linstall --version` / `poetry run linstall --help`\n- `poetry check`\n\n## Notes\n\n- Poetry:\n  - [Install/Uninstall Poetry](https://python-poetry.org/docs/master/#installation)\n  - `curl -sSL https://install.python-poetry.org | python3 - --preview`\n  - `poetry --version`\n  - `poetry config --list`\n  - `poetry config virtualenvs.in-project true`\n  - Dependencies:\n    - Add the dependencies and just leave the version number in the `pyproject.toml` file for exact versions\n    - `poetry add click markdown-subtemplate pyperclip`\n    - `poetry add black isort flakeheaven flake8-use-fstring --group dev`\n  - Delete the virtual environment: `poetry env remove python` ([source](https://github.com/python-poetry/poetry/issues/926#issuecomment-710056079))\n- [Poetry Version Plugin](https://github.com/tiangolo/poetry-version-plugin):\n  - `poetry self add poetry-version-plugin`\n  - `poetry build`\n  - `poetry self remove poetry-version-plugin`\n  - [plugin does not work anymore with latest poetry 1.2.0b2](https://github.com/tiangolo/poetry-version-plugin/issues/25) (open) issue.\n- [FlakeHeaven](https://github.com/flakeheaven/flakeheaven):\n  - `poetry run flakeheaven missed`\n  - `poetry run flakeheaven plugins`\n  - `poetry run flakeheaven config` / `poetry run flakeheaven config --plugins-only`\n  - `poetry run flakeheaven lint ./linstall/` / `poetry run flakeheaven lint --help`\n  - By default, FlakeHeaven runs only `pyflakes` and `pycodestyle` ([source](https://flakeheaven.readthedocs.io/en/latest/config.html) and [source](https://flakeheaven.readthedocs.io/en/latest/plugins.html))\n  - [IDE integration](https://flakeheaven.readthedocs.io/en/latest/ide.html) documentation\n  - [IDE Integration fails on VSCode](https://github.com/flakeheaven/flakeheaven/issues/32) (open) issue and [BUG: flake8heavened just runs flake8 in VSCode](https://github.com/flakeheaven/flakeheaven/issues/127) issue\n  - `poetry run flakeheaven code FS001` ([source](https://flakeheaven.readthedocs.io/en/latest/commands/code.html))\n  - `poetry run flakeheaven codes flake8-use-fstring` ([source](https://flakeheaven.readthedocs.io/en/latest/commands/codes.html))\n- Commands:\n  - Python:\n    - [pip](https://pip.pypa.io/en/stable/cli/pip_install/): `pip install`\n    - [Pipenv](https://pipenv.pypa.io/en/latest/install/#installing-packages-for-your-project): `pipenv install`\n    - [Poetry](https://python-poetry.org/docs/master/cli/#add): `poetry add`\n    - [PDM](https://python-poetry.org/docs/master/cli/#add) ([example](https://github.com/pdm-project/pdm#quickstart)): `pdm add`\n    - [Pyflow](https://github.com/David-OConnor/pyflow#what-you-can-do): `pyflow install`\n- [shellingham](https://github.com/sarugaku/shellingham)\n',
    'author': 'João Palmeiro',
    'author_email': 'joaopalmeiro@proton.me',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/joaopalmeiro/linstall',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
