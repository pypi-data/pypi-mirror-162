# CONSIGLIERE

A library for building Telegram apps.

[![PyPI](https://img.shields.io/pypi/v/consigliere?color=gold)](https://pypi.org/project/consigliere/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/consigliere?color=gold&label=dpm)](https://pypi.org/project/consigliere/)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Maintainability](https://api.codeclimate.com/v1/badges/4164098b73754a3eda4b/maintainability)](https://codeclimate.com/github/tgrx/consigliere/maintainability)
[![Lines of code](https://img.shields.io/tokei/lines/github/tgrx/consigliere)](https://github.com/tgrx/consigliere/tree/main)
[![main](https://github.com/tgrx/consigliere/actions/workflows/development.yaml/badge.svg?branch=main)](https://github.com/tgrx/consigliere/actions)
[![codecov](https://codecov.io/gh/tgrx/consigliere/branch/main/graph/badge.svg?token=SNEY3K22KI)](https://codecov.io/gh/tgrx/consigliere)

## Packages
[![pydantic](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/pydantic?color=white)](https://pydantic-docs.helpmanual.io/)

[![black](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/black?color=white)](https://black.readthedocs.io/en/stable/)
[![flake8](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/flake8?color=white)](https://flake8.pycqa.org/en/latest/)
[![isort](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/isort?color=white)](https://pycqa.github.io/isort/)
[![mypy](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/mypy?color=white)](https://mypy.readthedocs.io/en/stable/)
[![pylint](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/pylint?color=white)](https://www.pylint.org/)
[![pytest](https://img.shields.io/github/pipenv/locked/dependency-version/tgrx/alpha/dev/pytest?color=white)](https://docs.pytest.org/en/6.2.x/)

---

## Terms and shortcuts

- API
    [Telegram Bot API](https://core.telegram.org/bots/api)]

## Mission

The mission of this library is to provide a strict interface for the API.
By *strict* we mean that all types and methods in the library interface maps to those described in the API docs.

You won't meet any auxiliary stuff like sophisticated OOP patterns,
obscure event loops and listeners and that like kind of stuff.

API types are Pydantic models with strict type hints.
API methods are pure Python functions which accept params with exactly the same type as described in API.
Any optional field/param are marked as `Optional` in the code, so don't be afraid of tri-state bool types :)
