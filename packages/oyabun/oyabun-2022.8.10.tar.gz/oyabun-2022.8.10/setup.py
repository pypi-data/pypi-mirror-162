# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oyabun', 'oyabun.telegram']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp[speedups]>=3.8.1,<4.0.0',
 'httpx>=0.23.0,<0.24.0',
 'orjson>=3.7.11,<4.0.0',
 'pydantic[dotenv]>=1.9.1,<2.0.0']

setup_kwargs = {
    'name': 'oyabun',
    'version': '2022.8.10',
    'description': 'Telegram bare-metal lib',
    'long_description': "# CONSIGLIERE\n\nA library for building Telegram apps.\n\n[![PyPI](https://img.shields.io/pypi/v/consigliere?color=gold)](https://pypi.org/project/consigliere/)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/consigliere?color=gold&label=dpm)](https://pypi.org/project/consigliere/)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Maintainability](https://api.codeclimate.com/v1/badges/4164098b73754a3eda4b/maintainability)](https://codeclimate.com/github/tgrx/consigliere/maintainability)\n[![Lines of code](https://img.shields.io/tokei/lines/github/tgrx/consigliere)](https://github.com/tgrx/consigliere/tree/main)\n[![main](https://github.com/tgrx/consigliere/actions/workflows/development.yaml/badge.svg?branch=main)](https://github.com/tgrx/consigliere/actions)\n[![codecov](https://codecov.io/gh/tgrx/consigliere/branch/main/graph/badge.svg?token=SNEY3K22KI)](https://codecov.io/gh/tgrx/consigliere)\n\n## Packages\n[![pydantic](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/pydantic?color=white)](https://pydantic-docs.helpmanual.io/)\n\n[![black](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/black?color=white)](https://black.readthedocs.io/en/stable/)\n[![flake8](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/flake8?color=white)](https://flake8.pycqa.org/en/latest/)\n[![isort](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/isort?color=white)](https://pycqa.github.io/isort/)\n[![mypy](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/mypy?color=white)](https://mypy.readthedocs.io/en/stable/)\n[![pylint](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/pylint?color=white)](https://www.pylint.org/)\n[![pytest](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/pytest?color=white)](https://docs.pytest.org/en/6.2.x/)\n\n---\n\n## Terms and shortcuts\n\n- API\n    [Telegram Bot API](https://core.telegram.org/bots/api)]\n\n## Mission\n\nThe mission of this library is to provide a strict interface for the API.\nBy *strict* we mean that all types and methods in the library interface maps to those described in the API docs.\n\nYou won't meet any auxiliary stuff like sophisticated OOP patterns,\nobscure event loops and listeners and that like kind of stuff.\n\nAPI types are Pydantic models with strict type hints.\nAPI methods are pure Python functions which accept params with exactly the same type as described in API.\nAny optional field/param are marked as `Optional` in the code, so don't be afraid of tri-state bool types :)\n",
    'author': 'Alexander Sidorov',
    'author_email': 'alexander@sidorov.dev',
    'maintainer': 'Alexander Sidorov',
    'maintainer_email': 'alexander@sidorov.dev',
    'url': 'https://github.com/tgrx/oyabun',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
