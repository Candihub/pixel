# Pixel

[![CircleCI](https://circleci.com/gh/Candihub/pixel.svg?style=svg)](https://circleci.com/gh/Candihub/pixel)
[![Coverage Status](https://coveralls.io/repos/github/Candihub/pixel/badge.svg)](https://coveralls.io/github/Candihub/pixel)

## Requirements

* Python 3.6+
* [Pipenv](https://docs.pipenv.org)


_Nota bene_: to install and use Pipenv, we invite you to read the [project
documentation](https://docs.pipenv.org). In most cases, installing it can be
resumed to:

```bash
$ pip3 install --user --upgrade pipenv
```

Mac OS X users may rather consider using the following command:

```bash
$ sudo -H pip3 install --upgrade pipenv
```

## Quick start

```bash
# Clone the project
$ git clone git@github.com:Candihub/pixel.git
$ cd pixel
# Install project dependencies (production & development)
$ pipenv install --dev
# Create a development database
$ pipenv run ./manage.py migrate
# Run the django development server:
$ pipenv run ./manage.py runserver
```

Open your favorite browser with the following url: http://127.0.0.1:8000 and it
should work™.

## Run the tests

Project tests use pytest. To run them in your virtualenv, use Pipenv as follow:

```bash
$ pipenv run py.test
```

## Lint the code

This project use `flake8` to ensure coding style consistency (PEP8). To run it
in your virtualenv, use Pipenv as follow:

```bash
$ pipenv run flake8
```

## Contributing

Please, see the [CONTRIBUTING](CONTRIBUTING.md) file.

## Contributor Code of Conduct

Please note that this project is released with a [Contributor Code of
Conduct](http://contributor-covenant.org/). By participating in this project you
agree to abide by its terms. See [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) file.

## License

Monod is released under the BSD-3 License. See the bundled [LICENSE](LICENSE)
file for details.
