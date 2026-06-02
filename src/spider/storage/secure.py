"""
Token-protected attachment storage.

- When OBJECT_STORAGE_ENABLED: store files in S3/MinIO; url() returns a path
  that goes through the secure view (presigned redirect).
- When disabled: store files in MEDIA_ROOT; url() still returns the secure path
  so the view can stream from disk.
"""

from urllib.parse import urlencode

from django.conf import settings
from django.core.files.storage import FileSystemStorage


def _secure_attachment_url(name):
    """Build the secure attachment URL path (no direct S3/filesystem URL)."""
    if not name:
        return ""
    path = settings.SECURE_ATTACHMENT_URL_PATH.rstrip("/")
    return f"{path}?{urlencode({'path': name})}"


class SecureURLMixin:
    """Mixin that makes storage return secure view URL instead of direct file URL."""

    def url(self, name):
        return _secure_attachment_url(name)


class SecureFileSystemStorage(SecureURLMixin, FileSystemStorage):
    """
    Filesystem storage that still exposes files only via the secure view.
    Used when OBJECT_STORAGE_ENABLED is False (e.g. local dev).
    Files are stored in PRIVATE_MEDIA_ROOT, which is never added to urlpatterns.
    """

    def __init__(self, **kwargs):
        location = getattr(settings, "PRIVATE_MEDIA_ROOT", None)
        if not location:
            import os

            location = os.path.join(settings.MEDIA_ROOT, "private")
        kwargs.setdefault("location", location)
        kwargs.setdefault("base_url", "")
        super().__init__(**kwargs)


def get_secure_attachment_storage():
    if getattr(settings, "OBJECT_STORAGE_ENABLED", False):
        from .s3 import SecureS3Storage

        return SecureS3Storage()
    return SecureFileSystemStorage()
