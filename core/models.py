from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating ``created`` and
    ``modified`` fields.
    """

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        """
        When we define a new class that inherits from it, Django doesn’t
        create a core_timestampedmodel table when migrate is run.
        """

        abstract = True


class TitleAndTimeStampedModel(TimeStampedModel):
    title = models.CharField(verbose_name=_('title'), max_length=100)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title
