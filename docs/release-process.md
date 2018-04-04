# Release Process

We follow the [Semantic Versioning 2.0.0](https://semver.org/) rules to release
Pixel and choose the best version numbers for each stable version. The different
releases can be found at: https://github.com/Candihub/pixel/releases.

In short, the version number is made of three digits, separated with a dot:
`x.y.z`:

* `x` is the number on the left and represents the _MAJOR_ version number. This
  number should be increased (by one) when a backward incompatible change is
  added in the project, hence this number does not often change. When you update
  this number, both the _MINOR_ and _PATCH_ numbers should be reset to 0;
* `y` (middle number) represents the _MINOR_ version number. This number should
  be increased (by one) every time **new features** are added to the project.
  When you update this number, the _PATCH_ number should be reset to 0;
* `x` (right number) represents the _PATCH_ version number. This number should
  be increased (by one) every time **bug fixes** are added to the project. If
  you have both new features and bug fixes, update the _MINOR_ version.

**Important:** be sure to be on the `master` branch and that your local
repository is up to date (run `git pull origin master` to get the latest changes
from the server).


## How to release a new version?

In order to release a new (stable) version (_e.g._, `1.1.0`), you must:

1. create a new branch, _e.g._ `release-1.1.0`
2. update the version number of the project by updating the following files:
   `VERSION`, `pixel/__init__.py`, `package.json` and `.zenodo.json`
3. update the `CHANGELOG` file with a description of the new features, bug
   fixes, and so on for the end users
4. commit the version changes as well as the updated `CHANGELOG` file (_e.g._,
   message could be `Prepare 1.1.0 release`)
5. push the branch on GitHub, open a PR, and wait for the CI status. The commit
   to prepare the release MUST pass (_i.e._ be "green")
6. tag the version locally (_e.g._, `git tag 1.1.0`)
7. push the tag to GitHub by using the `--tags` option on `git push`
8. go to https://github.com/Candihub/pixel/releases and create a GitHub release
   from the Git tag you've just pushed. Give a name to the release (at least the
   version number) and (ideally) copy/paste the content you've written in the
   `CHANGELOG`
9. merge the PR

Note: a _release_ is another name to refer to a _stable version_, because we
"release" stable versions only. All "releases" (or "stable versions") are tagged
in git, _i.e._ (Git) tags refer to releases.
