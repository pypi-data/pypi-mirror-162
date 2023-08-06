[![pipeline status](https://gitlab.com/biomedit/django-drf-utils/badges/master/pipeline.svg)](https://gitlab.com/biomedit/django-drf-utils/-/commits/master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![python version](https://img.shields.io/pypi/pyversions/django-drf-utils.svg)](https://pypi.org/project/django-drf-utils)
[![license](https://img.shields.io/badge/License-LGPLv3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![latest version](https://img.shields.io/pypi/v/django-drf-utils.svg)](https://pypi.org/project/django-drf-utils)

# django-drf-utils

## Releases

This project follows the [semantic versioning specification](https://semver.org/) for its releases.

## Development

### Requirements

- Python >=3.8
- Django >=3.2
- django-rest-framework >=3.12

### Setup

- Create and activate a python3 venv.
- Install the library in the editable mode `pip install -e .[test,stubs]`
- Install dev requirements `pip install -r requirements-dev.txt`.
- Install git hooks to automatically format code using black with `pre-commit install`

## Installation

### From git in `requirements.txt`

To install this package from this git repository, add the `django-drf-utils` package to the `requirements.txt` file.
