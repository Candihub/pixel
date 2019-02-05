## For deployment

## Prior the installation - concepts

The `Pixel` application is intensively built on containerization paradigm. It relies on `Docker`[^1]. Docker is a tool that packages an application and its dependencies in a virtual container. Developer build an image that contains everything. This image is downloaded on the host system and is used to build one or more independent instances. Each instance is fully isolated, named, and relies to the kernel's functionality.

Consequently, you can deploy on one host one or more isolated `Pixel` application. Each instance will use its own database and web server.

[^1]: https://docs.docker.com

### Minimal configuration and dependencies

`Pixel` application can be deployed on Linux and MacOS operating system. Deployment on Windows is possible, but this situation will not be described in this documentation.

Minimal requirements:

- 64 bits operating system (Linux / MacOS)
- Docker community edition > v18
- Access to the internet (require for Docker images download)
- [optional] a web server (Apache or Nginx) that is configured as a reverse proxy

### Architecture overview

#### One `Pixel` application: three containers

`Pixel` is a web application built using the Python Django framework[^2]. This framework is based on a model-view-controller architecture pattern. The application requires a database and we choose PostgreSQL[^3]. Django suits well to develop high quality applications but if it comes with a built-in web server, we cannot use it to serve the application efficiently, especially static files.  

![Figure 1 - Architecture](docs/images/Figure-1.png)

[^2]: https://www.djangoproject.com
[^3]: https://www.postgresql.org

#### Container instances versus docker image

`Pixel` authors have built a docker image for the `Pixel` application. Other containers, `Nginx` and `PostgreSQL` rely on official docker image.

On one host (operating system) you can deploy one or multiples `Pixel` applications. Please notice that each installation / deployment will result in the creation / execution of three docker instances:

1. One for the `Pixel` application
2. One for the `PostreSQL` database 
3. One for the `Nginx` web server

In case of multiple installations, each trio of docker instances if fully isolated: data are not shared across `Pixel` installation.

![Figure 2 - docker images, docker instances](docs/images/Figure-2.png)


## Deployment

This section describes configuration files and way to deploy the `Pixel` application.

### Specific user

We recommend creating a dedicated user to deploy `Pixel`. It will allow you to deploy:

- a specific version of `Pixel`
- set all environment variables (database account and password configuration)
- easily update the software when a new version is released

The minimal directory should have this organization:

```
.
├── bin
│   └── deploy # script that will be executed to deploy Pixel application
├── docker-compose.yml # docker instance configuration file
└── .env # environment variables used during deployment
```

### Files description

#### The .env file

The `.env` file contains environment variables used by docker to  instantiate containers and setup the Django application. The file is divided in three sections:

- Django specific environment variable
- PostgreSQL environment variables
  - host name
  - database name
  - PostgreSQL user name
  - PostgreSQL user password
- Docker
  - Version to use for container instantiation
- SMTP server configuration (notification)
  - host
  - port
  - user name
  - user password

The `.env` file looks like:

```
# Django
DJANGO_SETTINGS_MODULE=pixel.settings
DJANGO_CONFIGURATION=Production
DJANGO_SECRET_KEY=<GENERATE-A-SECRET-KEY-HERE>

# Database
POSTGRES_HOST=db 
POSTGRES_DB=pixel
POSTGRES_USER=pixel
POSTGRES_PASSWORD=<GENERATE-A-PASSWORD-HERE>

# Docker
VERSION=4.0.0

# Email
EMAIL_HOST=<SMTP-SERVER-HOST-NAME-OR-IP>
EMAIL_PORT=<SMTP-PORT>
EMAIL_HOST_USER=<SMTP-USERNAME>
EMAIL_HOST_PASSWORD=<YOUR-SMTP-PASSWORD-HERE>
```

You must generate two secret keys:

- one for the Django application `DJANGO_SECRET_KEY`
- one for the PostgreSQL user `POSTGRES_PASSWORD`

For email notification, SMTP credentials are required.

#### The docker-compose.yml file

The `docker-compose.yml` is the most important file. This file formatted in the YAML format (YAML stands for "YAML Ain't Markup Language") and it is used to configure:

- docker container images that will be downloaded and launched
- dependencies between these docker instances
- interaction between system file system and the docker file system (i.e. which file from the file system will be accessible from the docker instance)

```
version: '2.1'

services:
  db:
    image: postgres:9.6
    env_file: .env

  web:
    image: "candihub/pixel:${VERSION:-latest}"
    env_file: .env
    volumes:
      - media:/app/pixel/public/media
      - run:/app/pixel/run
      - static:/app/pixel/public/static
    depends_on:
      - db

  proxy:
    image: nginx
    volumes:
      - ./docker/etc/nginx/conf.d/pixel.conf:/etc/nginx/conf.d/default.conf:ro
      - media:/app/pixel/public/media:ro
      - run:/app/pixel/run:ro
      - static:/app/pixel/public/static:ro
    ports:
      - 8902:80
    depends_on:
      - web

volumes:
  media:
    name: pixel-production-media
  run:
    name: pixel-production-run
  static:
    name: pixel-production-static
```

As mentioned in the global architecture presentation, `Pixel` is built on three different kind of services:

- a web server `Nginx`
- an object-relational database management system `PostgreSQL`
- a web application built with Django called `Pixel`

These three services are sufficient for `Pixel` to go live. They will be instantiated through the `Docker` container engine.

The `docker-compose.yml` file is divided in two parts:

1. Description of services / docker instances
2. Description of `volumes`: data location

We need three services (Nginx, PostgreSQL, `Pixel` web application). Accordingly, the `docker-compose.yml` file in the `services` section describes the way docker will download a docker image and will instantiate the corresponding `docker instance`. 

The first service is the PostgreSQL database:

```
db:
    image: postgres:9.6
    env_file: .env
```

Its description is obvious. We ask for the version `9.6` of the docker image called `postgres` and we specify that all environment variables required to instantiate the database are specified in the `.env` file. The `postgres` image will be downloaded from the original repository (https://hub.docker.com/_/postgres/).

The second service is the `Pixel` web application

```
web:
    image: "candihub/pixel:4.0.0"
    env_file: .env
    volumes:
      - media:/app/pixel/public/media
      - run:/app/pixel/run
      - static:/app/pixel/public/static
    depends_on:
      - db
```

Same thing here. The `Pixel` web application will be downloaded from the docker hub repository (hub.docker.com/r/candihub/pixel), using the stable version/tag 4.0.0. Environment variables are passed through the `.env` file. In addition, three volumes are specified (they mainly contains static files served by the web server). Finally, the instantiation of this docker instance is linked to the instantiation of the PostgreSQL database.

Web application generates web pages on the fly but requires access to static files (images / CSS and so on). We expose to the instance some specific paths: media, run and static directories.

Earlier in this document, we emphasize the role of the `Nginx` web server instance that is in charge of static files serving. This overlay between the user and the web application is called a `proxy` web server. We choose `Nginx` that is the flagship server for this role.

This is described in this section:

```
  proxy:
    image: nginx
    volumes:
      - ./docker/etc/nginx/conf.d/pixel.conf:/etc/nginx/conf.d/default.conf:ro
      - media:/app/pixel/public/media:ro
      - run:/app/pixel/run:ro
      - static:/app/pixel/public/static:ro
    ports:
      - 8902:80
    depends_on:
      - web
```

We use the standard and latest `nginx` image downloaded from the official repository (https://hub.docker.com/_/nginx/).

Two important sections here:

1. `volumes` that gives a read-only access to:
   -  static file directories: media, run, static
   -  shared directory between the host file system and the docker instance in order to configure for the `Nginx` web server
2. `ports` that exposes external port. Here we expose the port 80 of the docker instance to the host's port 8082. A request on port 8902 of the host will be propagated to the port 80 of the docker instance.

Finally, we specify the dependency between this instance and the web application instance called `web` with the `depends_on` section.

### Deploy script

```
function docker_compose() {
    docker-compose -p pixel-[your-specific-id] "$@"
}

function django_admin() {
    docker_compose exec web pipenv run python ./manage.py "$@"
}

if [[ "$#" -eq "1" ]] ; then
    sed -i -e "s/^VERSION=.*/VERSION=$1/" .env
    echo "set VERSION to $1"
fi

docker_compose pull web
docker_compose up -d --force-recreate proxy web
django_admin collectstatic --noinput --clear
django_admin migrate
```

All docker instances will have the prefix ```pixel-[your-specific-id]```. This allows you to deploy - on the same host - multiples Pixel applications with a convenient naming system.

This script launch four commands:

1. Pull the image of pixel (web, see docker-composer file)
2. Launch all instances (web, db and proxy) recreating the proxy and web instances - not then database of course (this will delete all data)
3. Collect all static file from the Django app. These files will be served by the proxy instance
4. Migrate the database if needed

### Host installation using host's Nginx web server as a reverse proxy

#### Configure Pixel web application with your hostname

Django must be configured with a specific hostname.

```
docker cp [your-pixel-web-instance-name-or-id]:/app/pixel/pixel .
```

On the local file, please update the ```ALLOWED_HOSTS``` variable and ```EMAIL_SUBJECT_PREFIX```:

```
class Production(Staging):

    ALLOWED_HOSTS = ['pixel.data-fun.io', ]
    EMAIL_SUBJECT_PREFIX = '[Pixel/Data-Fun.io] '
```

Then copy this modified file to the docker file system:

```
docker cp settings.py [your-pixel-web-instance-name-or-id]:/app/pixel/pixel/settings.py
```

Finally, restart the instance:

```
docker restart [your-pixel-web-instance-name-or-id]
```

#### Login on the Pixel docker instance

You can launch a bash shell in the Pixel docker instance using this command:

```
docker exec -it [your-pixel-web-instance-name-or-id] bash
```

#### Interact with Django using manage.py

You should use the `piping run command` to launch a python interpreter in the Docker instance. This command configures the PythonPath.

```
pipenv run python ./manage.py
```

Open a shell:

```pipenv run python ./manage.py shell```

Create the super user:

```pipenv run python ./manage.py createsuperuser```