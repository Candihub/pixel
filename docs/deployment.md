# Deployment / Migration

## Deploy

The `production` environment, available at https://pixel.candihub.eu/, can be
deployed on any new tag created, but it is not automatically deployed.
Circle-CI builds a Docker image (tagged with the Git tag of the release).

On the server, deployment is performed using the following bash script:

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

## Server settings

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
