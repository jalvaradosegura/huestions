from django.db import models
from django.contrib.auth.models import AbstractUser

from questions.models import Alternative


class CustomUser(AbstractUser):
    alternatives_chosen = models.ForeignKey(
        Alternative,
        on_delete=models.CASCADE,
        related_name='users',
        blank=True,
        null=True
    )
