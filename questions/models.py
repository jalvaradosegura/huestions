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

    def get_amount_of_users_that_have_voted(self):
        return sum(self.get_votes_amount_for_each_alternative())

    def get_votes_amount_for_each_alternative(self):
        return [
            alternative.get_votes_amount()
            for alternative in self.alternatives.all()
        ]

    def get_votes_percentage_for_each_alternative(self):
        return [
            alternative.get_votes_percentage()
            for alternative in self.alternatives.all()
        ]


class Alternative(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='alternatives'
    )
    alternative = models.CharField(max_length=100)

    def __str__(self):
        return self.alternative

    def get_votes_amount(self):
        return self.users.all().count()

    def get_votes_percentage(self):
        return (
            self.get_votes_amount()
            / self.question.get_amount_of_users_that_have_voted()
            * 100
        )
