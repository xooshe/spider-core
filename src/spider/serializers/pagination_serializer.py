from rest_framework import serializers

from spider.dataclasses import PaginationRO


class PaginationInfoSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    take = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_items = serializers.IntegerField()
