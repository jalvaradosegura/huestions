from django.core.exceptions import ValidationError

from core.constants import MAX_IMAGE_SIZE


def file_size_validator(value):
    if value.size > MAX_IMAGE_SIZE:
        raise ValidationError('File too large. Size should not exceed 2 MiB.')
