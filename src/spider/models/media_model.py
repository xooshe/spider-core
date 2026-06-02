import uuid

from django.db import models, transaction

from .enums import MediaTypes


class MediaModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField(
        upload_to=f"media/{__build_class__.__name__}", blank=True, null=True
    )
    alt = models.CharField(max_length=128, blank=True)
    type = models.CharField(
        max_length=32,
        choices=MediaTypes.CHOICES,
        default=MediaTypes.IMAGE,
    )
    external_url = models.CharField(max_length=256, blank=True, null=True)
    oembed_data = models.JSONField(blank=True, default=dict)

    @transaction.atomic
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.alt} | [{self.id}]"

    class Meta:
        abstract = True
