from django.contrib.auth.models import AbstractUser
from django.db import models

from questions.models import Alternative


class CustomUser(AbstractUser):
    alternatives_chosen = models.ManyToManyField(
        Alternative, related_name='users', blank=True
    )

    def get_amount_of_lists_created(self):
        return self.lists.count()

    def get_amount_of_questions_answered(self):
        return self.alternatives_chosen.count()
