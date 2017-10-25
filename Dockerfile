FROM python:3.6

# Development build
ARG IS_NOT_PRODUCTION

# Install Pipenv
RUN pip install pipenv --upgrade

# Add a non-privileged user for installing and running
# the application
RUN groupadd --gid 10001 app && \
    useradd --uid 10001 --gid 10001 --home /app --create-home app

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

# docker run commands within enabled pipenv
ENTRYPOINT ["pipenv", "run"]
CMD ["gunicorn", "-c", "/usr/local/etc/gunicorn/pixel.py", "pixel.wsgi:application"]
