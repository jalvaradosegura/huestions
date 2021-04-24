from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.constants import DEFAULT_IMAGE_NAME
from questions.utils import (
    reshape_img_to_square_with_blurry_bg,
    reshape_img_to_square_with_blurry_bg_gcp,
)


class DemoList(models.Model):
    title = models.CharField(verbose_name=_('title'), max_length=100)

    def __str__(self):
        return self.title


class DemoQuestion(models.Model):
    title = models.CharField(verbose_name=_('title'), max_length=100)
    child_of = models.ForeignKey(
        DemoList, on_delete=models.CASCADE, related_name='questions'
    )

    def __str__(self):
        return self.title


class DemoAlternative(models.Model):
    title = models.CharField(
        verbose_name=_('title'), max_length=100, default=''
    )
    question = models.ForeignKey(
        DemoQuestion, on_delete=models.CASCADE, related_name='alternatives'
    )
    image = models.ImageField(
        default=DEFAULT_IMAGE_NAME, upload_to='alternative_pics'
    )
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if settings.STORE_IN_BUCKET:
            reshape_img_to_square_with_blurry_bg_gcp(self.image.name)
        else:
            bg_img = reshape_img_to_square_with_blurry_bg(self.image.path)
            bg_img.save(self.image.path)
