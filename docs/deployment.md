# Deployment

This document describes the (automated) deployment process of Pixel with
Circle-CI (please refer to [the Circle-CI documentation](circle-ci.md) for more
information about it).


## Continuous deployment in staging

The `staging` environment, available at https://staging.pixel.candihub.eu/, is
**deployed automatically on each new commit to the `master` branch**. Circle-CI
builds a Docker image (tag: `latest`) and runs the script below over SSH:

``` bash
#!/usr/bin/env bash

function docker_compose() {
    docker-compose -p pixel-staging "$@"
}

function django_admin() {
    docker_compose exec web pipenv run python ./manage.py "$@"
}

# 1. retrieve the latest version of the Pixel application (Docker image)
docker_compose pull web

# 2. restart the Pixel application (`web`) and the `proxy` container (because it
# exposes a socket that is created in the `web` container)
docker_compose up -d --no-deps --force-recreate proxy web

# 3. make sure to serve the latest static files using the `proxy` container
django_admin collectstatic --noinput --clear

# 4. run the database migrations to update the database schema (if any)
django_admin migrate
```

## Continuous delivery in production

The `production` environment, available at https://pixel.candihub.eu/, can be
deployed on any new tag created, but it is not automatically deployed.
Circle-CI builds a Docker image (tagged with the Git tag of the release), and
[asks for
approval](https://circleci.com/docs/2.0/workflows/#holding-a-workflow-for-a-manual-approval)
to deploy it to the production server. The script below is executed over SSH
with the tag as unique argument:

``` bash
#!/usr/bin/env bash

function docker_compose() {
    docker-compose -p pixel-production "$@"
}

function django_admin() {
    docker_compose exec web pipenv run python ./manage.py "$@"
}

if [[ "$#" -eq "1" ]] ; then
    sed -i -e "s/^VERSION=.*/VERSION=$1/" .env
    echo "set VERSION to $1"
fi

# 1. retrieve the latest tagged version of the Pixel application (Docker image)
docker_compose pull web

# 2. restart the Pixel application (`web`) and the `proxy` container (because it
# exposes a socket that is created in the `web` container)
docker_compose up -d --no-deps --force-recreate proxy web

# 3. make sure to serve the latest static files using the `proxy` container
django_admin collectstatic --noinput --clear

# 4. run the database migrations to update the database schema (if any)
django_admin migrate
```

You can see the Circle-CI workflows at:
https://circleci.com/gh/Candihub/workflows/pixel.

### Server settings

The `pixel` account is used on the server and does not have any other rights
than being able to log in and to run `sudo bin/deploy`. SSH credentials are
stored in the Circle-CI settings (Settings > Candihub > pixel > SSH
Permissions).

#### Staging

The `staging` environment data lives in the `~/staging` folder:

```
staging/
├── bin
│   └── deploy
├── docker
│   └── etc
│       └── nginx
│           └── conf.d
│               └── pixel.conf
└── docker-compose.yml
```

The `docker/etc/nginx/conf.d/pixel.conf` can be found in this project (same
path). The `docker-compose.yml` file can be found in the root directory of this
project, under the name: `docker-compose.staging.yml`.

#### Production

The `production` environment data lives in the `~/production` folder:

```
production/
├── bin
│   └── deploy
├── docker
│   └── etc
│       └── nginx
│           └── conf.d
│               └── pixel.conf
└── docker-compose.yml
```

The `docker/etc/nginx/conf.d/pixel.conf` can be found in this project (same
path). The `docker-compose.yml` file can be found in the root directory of this
project, under the name: `docker-compose.production.yml`.
