"""
Storage backends for token-protected attachments.
All attachment URLs go through SECURE_ATTACHMENT_URL_PATH so files
are only accessible with valid user or admin auth.
"""

from django.conf import settings
from django.core.files.storage import default_storage

from .secure import get_secure_attachment_storage

__all__ = ["get_secure_attachment_storage"]
