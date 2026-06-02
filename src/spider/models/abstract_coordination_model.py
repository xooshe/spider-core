from django.db import models
from spider.models.base import Model


class LocationCoordinationModel(Model):
    x_point = models.FloatField(null=True, blank=True)
    y_point = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True
