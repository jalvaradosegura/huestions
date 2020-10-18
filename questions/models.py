import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

    def was_created_recently(self):
        return self.creation_date >= timezone.now() - datetime.timedelta(
            days=1
        )
