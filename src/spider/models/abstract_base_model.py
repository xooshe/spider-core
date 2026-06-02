import uuid

from django.db import models

from spider.models.abstract_created_at_model import AbstractCreatedAtModel


class AbstractBaseModel(AbstractCreatedAtModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField("active", default=False)
    priority = models.IntegerField(default=10000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority"]
        abstract = True

    def __str__(self):
        if hasattr(self, "name"):
            return f"{self.name} | [{self.pk}]"  # type: ignore
        return f"{self.__class__.__name__} | [{self.pk}]"
