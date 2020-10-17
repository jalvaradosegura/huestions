from django.db import models


class Question(models.Model):
    question = models.CharField(max_length=100)

    def __str__(self):
        return self.question
