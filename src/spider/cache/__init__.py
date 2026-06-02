import hashlib

from django.core.cache import *


def get_cache_key(obj, *args, **kwargs):
    from spider.models import Model, QuerySet

    if isinstance(obj, Model):
        return "MODEL|{}|{}|{}|{}".format(
            obj._meta.app_label, obj._meta.model_name, args, kwargs
        )
    elif isinstance(obj, QuerySet):
        return "MODEL|{}|{}|{}|{}".format(
            obj.model._meta.app_label, obj.model._meta.model_name, args, kwargs
        )
    return "{}|{}|{}".format(str(obj), args, kwargs)


def get_hashed_cache_key(obj, *args, __method="sha3_256", **kwargs):
    return hashlib.__getattribute__(__method)(
        get_cache_key(obj, *args, **kwargs).encode("UTF-8")
    ).hexdigest()
