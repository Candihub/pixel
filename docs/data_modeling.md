# Data Modeling

## Database schema

We use the `graph_models` management command from
[django-extensions](https://django-extensions.readthedocs.io/en/latest/graph_models.html)
to generate a Graphviz dot file that you can use to generate a PNG or SVG file
representing `core` application models:

```bash
$ pipenv run ./manage.py graph_models core | pbcopy
```

Paste content to http://viz-js.com to generate a representation of the
database schema.
