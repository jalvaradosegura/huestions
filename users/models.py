from django.contrib.auth.models import AbstractUser
from django.db import models

from questions.models import Alternative


class CustomUser(AbstractUser):
    alternatives_chosen = models.ManyToManyField(
            Alternative,
            related_name='users',
            blank=True
    )
