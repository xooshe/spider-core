from django.db.models import Model as DjangoModel
from .queryset import QuerySet


class Model(DjangoModel):
    objects = QuerySet.as_manager()

    class Meta:
        abstract = True

    def getattribute(self, filed):
        obj = self
        for key in filed.split("__"):
            obj = obj.__getattribute__(key)
        return obj
