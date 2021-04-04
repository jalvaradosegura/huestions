import datetime

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from core.constants import DEFAULT_IMAGE_NAME
from core.models import TitleAndTimeStampedModel
from lists.models import QuestionList
from .utils import reshape_img_to_square_with_blurry_bg


class Question(TitleAndTimeStampedModel):
    slug = models.SlugField(null=False, max_length=255)
    child_of = models.ForeignKey(
        QuestionList, on_delete=models.CASCADE, related_name='questions'
    )

    class Meta:
        ordering = ('id',)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'edit_question', args=[self.child_of.slug, self.slug, self.id]
        )

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
        if self.alternatives.filter(users=user):
            return True
        return False

    def is_completed(self):
        if self.alternatives.count() == 2:
            return True
        return False

    def get_user_voted_alternative(self, user):
        for alternative in self.alternatives.all():
            if user in alternative.users.all():
                return alternative
        return None


class Alternative(TitleAndTimeStampedModel):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='alternatives'
    )
    image = models.ImageField(
        default=DEFAULT_IMAGE_NAME, upload_to='alternative_pics'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        bg_img = reshape_img_to_square_with_blurry_bg(self.image.path)
        bg_img.save(self.image.path)

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
