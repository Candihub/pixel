import uuid

from django.db import models

from apps.core import mixins


class ModelWithUUID(mixins.UUIDModelMixin, models.Model):
    """UUID model"""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )


class ModelWithStandardID(models.Model, mixins.UUIDModelMixin):
    """Mock wrong MRO"""

    pass
