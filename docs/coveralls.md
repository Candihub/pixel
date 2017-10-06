# Coveralls

> Coveralls is a web service to help you track your code coverage over time, and
ensure that all your new code is fully covered.

This documentation contains notes about how we proceed to integrate and
configure coveralls for the Pixel project. **Once configured, those steps don't
have to be reproduced.**

## Setup

1. Go to https://coveralls.io and connnect with your GitHub account.
2. Activate the Pixel repository in [this view](https://coveralls.io/repos/new),
   by switching it on.
3. If you don't see target repository, make sure your organization is visible,
   or else, grant access via the *Update Github Access Settings* button (at the
   bottom of the new repository page).
4. Copy the repository token available from [repo
   settings](https://coveralls.io/github/Candihub/pixel/settings).

## CircleCI integration

1. Add a [new environment
   variable](https://circleci.com/gh/Candihub/pixel/edit#env-vars) to CircleCI
   settings:  `COVERALLS_REPO_TOKEN` with the repository token as value (see
   previous section).
2. Add `coveralls` to project development dependencies
3. Add a new `coverage` job (depending on test) in CircleCI configuration:

```yaml
version: 2
jobs:
  # [...]

  coverage:
    # [...]
    steps:
      # [...]
      - run:
          name: Report code coverage
          command: |
            pipenv run coveralls

workflows:
  version: 2

  backend:
    jobs:
      # [...]

      - coverage:
          requires:
            - test
```
