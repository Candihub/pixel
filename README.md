# Pixel

[![CircleCI](https://circleci.com/gh/Candihub/pixel.svg?style=svg)](https://circleci.com/gh/Candihub/pixel)
[![Coverage Status](https://coveralls.io/repos/github/Candihub/pixel/badge.svg)](https://coveralls.io/github/Candihub/pixel)

## Requirements

We use Docker to develop and run Pixel. We invite you to ensure you have
installed the following requirements before trying to bootstrap the application:

* [Docker 1.12.6+](https://docs.docker.com/engine/installation/)
* [Docker compose 1.9.0+](https://docs.docker.com/compose/install/)

> We recommend you to follow Docker's official documentations to install
required docker tools (see links above).

## Quick start

Have you read the "Requirements" section above?

```bash
# Clone the project
$ git clone git@github.com:Candihub/pixel.git
$ cd pixel
# Install front-end and back-end dependencies (production & development)
$ make bootstrap
# Create a development database
$ make migrate-db
# Run the Django development server & css build watcher
$ make dev
```

Open your favourite browser with the following url: http://127.0.0.1:8000 and it
should work™.

## Build css

Pixel uses sass-based styles. To compile and post-process them, use:

```bash
$ make build-css
```

## Run the tests

Project tests are using `pytest` within a docker container. To run them use:

```bash
$ make test
```

## Lint the code

This project use `flake8` to ensure coding style consistency (PEP8). To run it
within a docker container, use:

```bash
$ make lint
```

## Maintenance commands

Most commands from the `Makefile` can be used as shortcuts to `docker-compose`
invocations. A list of commonly used commands follows:

* `make migrate-db`: run database migrations
* `make run-server`: run Django development server
* `make stop-server`: stop Django development server
* `make restart-server`: restart `web` container (Django)

If you want more flexibility to run `docker-compose`-based commands, use:

```bash
$ bin/compose
# ☝️ an alias for:
# docker-compose -f docker-compose.yml -p pixel-dev

$ bin/manage
# ☝️ an alias for:
# docker-compose -f docker-compose.yml -p pixel-dev \
#   run --rm web python manage.py
```

## Contributing

Please, see the [CONTRIBUTING](CONTRIBUTING.md) file.

## Contributor Code of Conduct

Please note that this project is released with a [Contributor Code of
Conduct](http://contributor-covenant.org/). By participating in this project you
agree to abide by its terms. See [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md) file.

## License

Pixel is released under the BSD-3 License. See the bundled [LICENSE](LICENSE)
file for details.
