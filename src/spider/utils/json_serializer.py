from django.core.serializers.json import DjangoJSONEncoder


class DefaultJsonEncoder(DjangoJSONEncoder):
    def default(self, obj):
        return super().default(obj)
