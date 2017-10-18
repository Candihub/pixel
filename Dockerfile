FROM python:3.6

# Install Pipenv
RUN pip install pipenv --upgrade

# add a non-privileged user for installing and running
# the application
RUN groupadd --gid 10001 app && \
    useradd --uid 10001 --gid 10001 --home /app --create-home app

WORKDIR /app

# Install python requirements
COPY Makefile Makefile
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN su app -c "make install" && \
    rm -fr /app/.cache/pip

COPY . /app/

# Gunicorn
RUN mkdir -p /usr/local/etc/gunicorn
COPY docker/usr/local/etc/gunicorn/pixel.py /usr/local/etc/gunicorn/pixel.py
RUN su app -c "mkdir run"

EXPOSE 80

USER app
ENTRYPOINT ["pipenv", "run"]
CMD ["gunicorn", "-c", "/usr/local/etc/gunicorn/pixel.py", "pixel.wsgi:application"]
