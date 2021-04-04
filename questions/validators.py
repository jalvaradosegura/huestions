import os

from django.core.exceptions import ValidationError

from core.constants import (
    FILE_EXTENSION_ERROR,
    FILE_TOO_LARGE_ERROR,
    IMAGE_VALID_EXTENSIONS,
    MAX_IMAGE_SIZE,
)


def file_size_validator(value):
    if value.size > MAX_IMAGE_SIZE:
        raise ValidationError(FILE_TOO_LARGE_ERROR)


def file_extension_validator(value):
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in IMAGE_VALID_EXTENSIONS:
        raise ValidationError(FILE_EXTENSION_ERROR)
