from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import TitleAndTimeStampedModel

from .managers import ActivatedListManager


class QuestionList(TitleAndTimeStampedModel):
    slug = models.SlugField(unique=True, null=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='lists',
    )
    active = models.BooleanField(default=False)

    objects = models.Manager()
    activated_lists = ActivatedListManager()

    def get_absolute_url(self):
        return reverse('answer_list', args=[str(self.slug)])

    def _generate_unique_slug_if_needed(self):
        slug = slugify(self.title)
        num = 1
        while QuestionList.objects.filter(slug=slug).exists():
            slug = slugify(self.title) + f'-{num}'
            num += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug_if_needed()
        super().save(*args, **kwargs)

    def activate(self):
        self.active = True

    def has_at_least_one_full_question(self):
        if self.questions.exists():
            for question in self.questions.all():
                if question.is_completed():
                    return True
        return False
