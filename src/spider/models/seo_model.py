import uuid

from django.core.validators import MaxLengthValidator
from django.db import models


class SeoModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seo_title = models.CharField(
        max_length=70, blank=True, null=True, validators=[MaxLengthValidator(70)]
    )
    seo_description = models.CharField(
        max_length=4000, blank=True, null=True, validators=[MaxLengthValidator(300)]
    )

    class Meta:
        abstract = True
