"""
S3/MinIO storage for token-protected attachments.
Uses OBJECT_STORAGE_* settings; url() returns secure view path, not direct S3 URL.
"""

from storages.backends.s3 import S3Storage

from .secure import SecureURLMixin, _secure_attachment_url


class SecureS3Storage(SecureURLMixin, S3Storage):
    """
    S3-compatible storage (AWS S3 or MinIO) that exposes files only via
    the secure view (presigned redirect after auth check).
    """

    def __init__(self, **kwargs):
        from django.conf import settings as s

        kwargs.setdefault("access_key", s.OBJECT_STORAGE_ACCESS_KEY_ID)
        kwargs.setdefault("secret_key", s.OBJECT_STORAGE_SECRET_ACCESS_KEY)
        kwargs.setdefault("bucket_name", s.OBJECT_STORAGE_BUCKET_NAME)
        kwargs.setdefault("endpoint_url", s.OBJECT_STORAGE_ENDPOINT_URL or None)
        kwargs.setdefault("region_name", s.OBJECT_STORAGE_REGION)
        kwargs.setdefault("use_ssl", s.OBJECT_STORAGE_USE_SSL)
        super().__init__(**kwargs)

    def url(self, name):
        return _secure_attachment_url(name)

    def generate_presigned_url(self, name, expiration=60):
        """Generate a short-lived presigned URL for the secure view to redirect to."""
        from storages.utils import clean_name

        name = self._normalize_name(clean_name(name))
        connection = self.connection
        return connection.meta.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": name},
            ExpiresIn=expiration,
        )
