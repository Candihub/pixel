# Circle-CI

## Integration steps

1. Login to [circleci.com](https://circleci.com) with your github account to
   ease github integration.
2. If you cannot see your organization in the upper-left corner of CircleCI
   pages, go to https://circleci.com/account and click the "Check permissions"
   link in the GitHub section.
3. Select the Candihub organization (upper-left selection menu) and go to the
   [project tab](https://circleci.com/projects/gh/Candihub).
4. Click on the "Add Project" button.
5. Select the Pixel project by clicking the "Setup project button" on its row.
6. Select:
    - Operating System: Linux
    - Platform: 2.0
    - Language: Python
7. Follow the "next steps" section instructions to create your
   `.circleci/config.yml` file.

And voilà!

## Configuration (`.circleci/config.yml`)

At the time of writing, Pipenv is not that easy to integrate with CircleCI. This
is mostly due to CircleCI restrictions on environment manipulation during
runtime (`$PATH`). Here are a few tips used to integrate Pipenv with CircleCI.

### Add the user base’s binary directory to your `PATH`

If Pipenv is installed in user mode, _e.g._:

```bash
$ pip3 install --user pipenv
```

… you will need to add user base's binary directory (_e.g._ `~/.local/bin`) to
the `PATH` by adding this step (before using `pipenv`):

```yaml
version: 2
jobs:

  build:
    # [...]
    steps:
      - run:
          name: Add Pipenv to the PATH
          command: |
            echo "export PATH=~/.local/bin:$PATH" >> $BASH_ENV
```

### Force virtualenv path

Pipenv creates virtualenvs for you when running for the first time in a project
directory. This virtualenv will be located into something like
`~/.local/share/virtualenvs/pixel-YcbOu4pz`. The project key (last part of the
PATH) is hardly predictable, but we need to add this virtualenv to the cache to
speed up tests (we will use this cache in CircleCI workflow to avoid installing
project dependencies at each step). One solution is to force the virtualenv path
as follow:

```yaml
version: 2
jobs:

  build:
    working_directory: ~/pixel
    docker:
      - image: circleci/python:3.6.1
        environment:
          PIPENV_VENV_IN_PROJECT: 1
    steps:
      # [...]
      - save_cache:
          paths:
            - ~/.local
            - ~/pixel/.venv
          key: backend-deps-v2-{{ .Branch }}-{{ checksum "Pipfile.lock" }}
```

In the `build` job, we define the `PIPENV_VENV_IN_PROJECT` environment variable
(injected in our container during runtime); as mentioned in [Pipenv
documentation](https://docs.pipenv.org/advanced.html#configuration-with-environment-variables),
this will force the creation of a virtualenv in a `.venv` directory of the
project. Perfect, now we need to add this directory (`~/pixel/.venv`) to the
cache and add this virtualenv binary directory to the `PATH` with the following step:

```yaml
version: 2
jobs:
  # [...]

  test:
    # [...]
    docker:
      - image: circleci/python:3.6.1
        environment:
          PIPENV_VENV_IN_PROJECT: 1
    steps:
      # [...]
      - run:
          name: Add Pipenv & installed tools to the PATH
          command: |
            echo "export PATH=~/.local/bin:~/pixel/.venv/bin:$PATH" >> $BASH_ENV
```

Please note that we need to define the `PIPENV_VENV_IN_PROJECT` in every job
that will use our cached virtualenv.
