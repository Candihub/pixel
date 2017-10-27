# Docker

Pixel's full stack can be run with Docker containers. We did our best to follows
Mozilla's [Dockerflow](https://github.com/mozilla-services/Dockerflow)
specifications.

## Main application container

Pixel's main container is a `python:3.6`-based container designed to run a
Django project with `gunicorn` as a WSGI server (see
[`Dockerfile`](../Dockerfile)).

Once `Pipenv` is installed and the non-privileged user `app` has been created,
we run every commands with this user account. The `app` user home directory is
`/app` and the application is installed in `/app/pixel`.

By default, when building this container, you will only install production
dependencies. If you need development tools (_e.g._ to run tests), you can add
the `--build-arg IS_NOT_PRODUCTION=true` to your build command:

```bash
$ docker build -t pixel:dev --build-arg IS_NOT_PRODUCTION=true .
```

To decrease the size of our container, we only copy what is required to run the
project. Ignored paths are listed in the `.dockerignore` file. You need to know
that the git repository (`.git`) and node dependencies (`node_modules`) are not
available in the built container.

The `ENTRYPOINT` of this container is `pipenv run` so that you can run commands
in your python virtual environment with the `docker run` command.

The default command runs `gunicorn`, the wsgi server.

TODO: add docs about gunicorn's socket in the `/app/pixel/run` directory.


## Docker compose

As Pixel requires at least two containers to run (web and database), we use
[Docker compose](https://docs.docker.com/compose/) to ease Pixel running in
various contexts (development, test, staging and production).

### `development`

The base Docker compose configuration (see
[`docker-compose.yml`](../docker-compose.yml)) links the Django project (`web`)
to a PostgreSQL database container (`db`) and overrides the default command to
run Django's development server. To smooth development workflow, the current
directory is mounted as a volume in the application directory (`/app/pixel`).

To run the development server with docker compose, type the following command:

```bash
$ docker-compose -p pixel-dev up
```

or use the following `Makefile` rule:

```bash
$ make run-server
```

### `test`

Test configuration (see [`docker-compose.test.yml`](../docker-compose.test.yml))
links a PostgreSQL container with the Django project (built with development
dependencies).

To run tests locally with docker compose, type the following command:

```bash
$ docker-compose -f docker-compose.test.yml -p pixel-test run --rm web pytest
```

or use the following `Makefile` rule:

```bash
$ make test
```

### `staging`

TODO

### `production`

TODO

## Continuous integration

The continuous integration workflow is composed of five steps:

1. Front-end build
2. Production back-end build
3. Development dependencies cache
4. Code lint
5. Code test

### Front-end build

We use a `node:8` base container to install front-end development tools with
yarn and build styles (stored in the `static` directory). This build is saved in
cache for further use (see next section).

### Production back-end build

This step is of utmost importance: it builds the `candihub/pixel` docker image
that we will use in next jobs (and hopefully in production). Once build, this
image tagged with the current branch is uploaded to the [Docker hub Pixel's
repository](https://hub.docker.com/r/candihub/pixel/).

> Note that we use the front-end job cache in this step to add compiled styles
to Pixel's docker image.

### Development dependencies cache

As our production build does not include the testing stack (`pytest`, etc.), we
need an extra step to install and cache them for further use.

### Code lint

We use Pixel's docker production image plus cached development dependencies on
top of it to run `flake8` (our code linter).

### Code test

Similarly to the code linting step, we use Pixel docker production image plus
cached development dependencies on top of it to run the test suite.

> nota bene: you will find a waiting loop hack with
[`dockerize`](https://github.com/jwilder/dockerize) for this job (before running
`pytest`), this hack is required to ensure that the `postgresql` container is
running, that the target database has been created and is fully operational.

## Continuous delivery

TODO

## Monitoring

TODO
