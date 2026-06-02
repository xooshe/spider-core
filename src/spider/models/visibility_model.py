import uuid

from django.db import models


class VisibilityModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    visibility = models.BooleanField(default=False)
    visible_in_list = models.BooleanField(default=False)
    searchable = models.BooleanField(default=False)
    expired_at = models.DateTimeField(null=True, blank=True)
    visible_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
