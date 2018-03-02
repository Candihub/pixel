# Data Modeling

## Models overview

We use the `graph_models` management command from
[django-extensions](https://django-extensions.readthedocs.io/en/latest/graph_models.html)
and [Graphviz](http://graphviz.org) to generate a SVG file representing Pixel
applications models:

```bash
$ bin/manage graph_models -E core data submission -X AbstractUser,TaggedModel,MPTTModel,TagModel | dot -T pdf -o ./docs/pixel-db.pdf
```

> _nota bene_: for clarification, we use the `-X` option to exclude models >
imported in applications `models.py`.


### A note on cached fields (PixelSet)

In the application, we display data that are expensive to compute because of the
different relation we have between the different models. In order to speed up the
application and provide a better user experience, we decided to create
`cached_*` fields on the `PixelSet` model. These fields are `array` of values,
which avoids to query them all the time (and we need them all the time).

These fields are created and populated on `PixelSet` creation, hence for regular
use, there should be no difference (importation works just fine). Yet, if you do
modify the information related to these `cached_*` fields, you should "update
the cached fields" in the Django admin:

- browse the `PixelSet` list at:
`https://pixel.example.org/admin/core/pixelset/`
- select the `PixelSet` to update by checking the checkbox on the left
- perform the "Update cached fields" (list) action
