from django.core.exceptions import ValidationError

from core.constants import FILE_TOO_LARGE, MAX_IMAGE_SIZE


def file_size_validator(value):
    if value.size > MAX_IMAGE_SIZE:
        raise ValidationError(FILE_TOO_LARGE)
