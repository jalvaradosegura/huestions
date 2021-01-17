import datetime

from django.db import models
from django.urls import reverse
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides selfupdating
    ``created`` and ``modified`` fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        """
        When we define a new class that inherits from it, Django doesn’t
        create a core_timestampedmodel table when migrate is run.
        """
        abstract = True


class Question(TimeStampedModel):
    question = models.CharField(max_length=100)

    def __str__(self):
        return self.question

    def get_absolute_url(self):
        return reverse('question_details', args=[str(self.id)])

    def was_created_recently(self):
        return self.created >= timezone.now() - datetime.timedelta(
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

    def has_the_user_already_voted(self, user):
        for alternative in self.alternatives.all():
            if user in alternative.users.all():
                return True
        return False


class Alternative(TimeStampedModel):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='alternatives'
    )
    alternative = models.CharField(max_length=100)

    def __str__(self):
        return self.alternative

    def get_votes_amount(self):
        return self.users.all().count()

    def get_votes_percentage(self):
        if self.question.get_amount_of_users_that_have_voted() == 0:
            return 0
        return (
            self.get_votes_amount()
            / self.question.get_amount_of_users_that_have_voted()
            * 100
        )
