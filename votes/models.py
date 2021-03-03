from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from questions.models import Alternative, Question, QuestionList


class Vote(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='votes',
    )
    list = models.ForeignKey(
        QuestionList,
        on_delete=models.SET_NULL,
        null=True,
        related_name='votes',
    )
    question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, related_name='votes'
    )
    alternative = models.ForeignKey(
        Alternative, on_delete=models.SET_NULL, null=True, related_name='votes'
    )

    def __str__(self):
        return f'{self.user} vote'
