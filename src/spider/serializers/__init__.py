from rest_framework.serializers import ModelSerializer as BaseModelSerializer
from spider.serializers.abstract_base_serializer import AbstractBaseSerializer


class ModelSerializer(AbstractBaseSerializer, BaseModelSerializer):
    pass
