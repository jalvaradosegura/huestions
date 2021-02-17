import datetime

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .managers import ActivatedListManager


class BaseAbstractModel(models.Model):
    """
    An abstract base class model that provides selfupdating
    ``created`` and ``modified`` fields.
    """

    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        """
        When we define a new class that inherits from it, Django doesn’t
        create a core_timestampedmodel table when migrate is run.
        """

        abstract = True

    def __str__(self):
        return self.title


class QuestionList(BaseAbstractModel):
    slug = models.SlugField(unique=True, null=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='lists'
    )
    active = models.BooleanField(default=False)

    objects = models.Manager()
    activated_lists = ActivatedListManager()

    def get_absolute_url(self):
        return reverse('questions_list_details', args=[str(self.slug)])

    def _generate_unique_slug_if_needed(self):
        slug = slugify(self.title)
        num = 1
        while QuestionList.objects.filter(slug=slug).exists():
            slug = slugify(self.title) + f'-{num}'
            num += 1
        return slug

    def save(self, *args, **kwargs):
        self.slug = self._generate_unique_slug_if_needed()
        super().save(*args, **kwargs)

    def activate(self):
        self.active = True

    def has_at_least_one_full_question(self):
        return True


class Question(BaseAbstractModel):
    slug = models.SlugField(null=False)
    child_of = models.ForeignKey(
        QuestionList, on_delete=models.CASCADE, related_name='questions'
    )

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('question_details', args=[str(self.id)])

    def was_created_recently(self):
        return self.created >= timezone.now() - datetime.timedelta(days=1)

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


class Alternative(BaseAbstractModel):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='alternatives'
    )

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

    def vote_for_this_alternative(self, user):
        self.users.add(user)
