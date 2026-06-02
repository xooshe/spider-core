from django.db import models

from .base import Model


class AbstractPropertyModel(Model):
    properties = models.TextField(blank=True, default="[]")

    class Meta:
        abstract = True
