FROM python:3.6

# Development build
ARG IS_NOT_PRODUCTION
# User/Group IDs
ARG UID=10001
ARG GID=10001

# Build-time metadata as defined at http://label-schema.org
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
LABEL org.label-schema.build-date=$BUILD_DATE \
    org.label-schema.name="Pixel" \
    org.label-schema.description="Integration of smart 'omics' data" \
    org.label-schema.url="https://pixel.candihub.eu/" \
    org.label-schema.vcs-ref=$VCS_REF \
    org.label-schema.vcs-url="https://github.com/Candihub/pixel/" \
    org.label-schema.vendor="CandiHub" \
    org.label-schema.version=$VERSION \
    org.label-schema.schema-version="1.0"

# Install Pipenv
RUN pip install pipenv --upgrade

# Add a non-privileged user for installing and running
# the application
RUN groupadd -f --gid $GID app && \
    useradd --uid $UID --gid $GID --home /app --create-home app

RUN su app -c "mkdir /app/pixel"

WORKDIR /app/pixel

# Install python requirements
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN su app -c "if [ -z $IS_NOT_PRODUCTION ]; then pipenv --bare install ; else pipenv --bare install -d ; fi" && \
    rm -fr /app/.cache/pip

COPY . /app/pixel

# Gunicorn
RUN mkdir -p /usr/local/etc/gunicorn
COPY docker/usr/local/etc/gunicorn/pixel.py /usr/local/etc/gunicorn/pixel.py
RUN su app -c "mkdir run"

USER app

# Create statics and media to serve
RUN mkdir -p public/media && \
    mkdir -p public/static

# Use fake Django environment to collectstatic
ENV DJANGO_SETTINGS_MODULE=pixel.settings \
    DJANGO_CONFIGURATION=Production \
    DJANGO_SECRET_KEY=ThisIsAFakeKeyUsedForBuildingPurpose

RUN pipenv run ./manage.py collectstatic -c

# docker run commands within enabled pipenv
ENTRYPOINT ["pipenv", "run"]
CMD ["gunicorn", "-c", "/usr/local/etc/gunicorn/pixel.py", "pixel.wsgi:application"]
