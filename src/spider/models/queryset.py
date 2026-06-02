from django.db import models
from django.db.models import QuerySet as DjangoQuerySet


class QuerySet(DjangoQuerySet): ...
