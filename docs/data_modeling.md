# Data Modeling

## Models overview

We use the `graph_models` management command from
[django-extensions](https://django-extensions.readthedocs.io/en/latest/graph_models.html)
to generate a Graphviz dot file that you can use to generate a PNG or SVG file
representing `core` application models:

```bash
$ pipenv run -- ./manage.py graph_models -E core -X AbstractUser,TaggedModel,MPTTModel,TagModel | pbcopy
```

> _nota bene_: for clarification, we use the `-X` option to exclude models
> imported in `core/models.py`.

Paste your clipboard content to http://viz-js.com to generate a projection of
Django models.
