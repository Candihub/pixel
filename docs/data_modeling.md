# Data Modeling

## Models overview

We use the `graph_models` management command from
[django-extensions](https://django-extensions.readthedocs.io/en/latest/graph_models.html)
and [Graphviz](http://graphviz.org) to generate a SVG file representing Pixel
applications models:

```bash
$ pipenv run -- ./manage.py graph_models -E core data -X AbstractUser,TaggedModel,MPTTModel,TagModel | dot -T pdf -o ./docs/pixel-db.pdf
```

> _nota bene_: for clarification, we use the `-X` option to exclude models >
imported in applications `models.py`.
