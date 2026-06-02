import uuid

from django.db import models

from spider.utils.json_serializer import DefaultJsonEncoder


class MetaDataModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    metadata = models.JSONField(
        blank=True, null=True, default=dict, encoder=DefaultJsonEncoder
    )

    class Meta:
        abstract = True
