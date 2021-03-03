from django.db import models
from django.conf import settings

from questions.models import QuestionList, Question, Alternative


class Vote(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
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
        related_name='votes'
    )
    question = models.ForeignKey(
        Question, on_delete=models.SET_NULL, null=True, related_name='votes'
    )
    alternative = models.ForeignKey(
        Alternative, on_delete=models.SET_NULL, null=True, related_name='votes'
    )

    def __str__(self):
        return f'{self.user} vote'
