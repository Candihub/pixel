import uuid

from django.utils.translation import ugettext as _


class UUIDModelMixin(object):

    def __str__(self):
        return self.get_short_uuid()

    def get_short_uuid(self):
        if not isinstance(self.id, uuid.UUID):
            raise TypeError(
                _("{} model id is not a valid UUID").format(
                    self.__class__.__name__
                )
            )
        return self.id.hex[:7]
