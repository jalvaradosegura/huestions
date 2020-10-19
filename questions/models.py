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


class Alternative(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='alternatives'
    )
    alternative = models.CharField(max_length=100)

    def __str__(self):
        return self.alternative
