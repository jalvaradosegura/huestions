from captcha.fields import ReCaptchaField
from django import forms
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils.translation import gettext_lazy as _

from core.constants import (
    LIST_COMPLETION_ERROR_MESSAGE,
    MAX_AND_MIN_LENGTH,
    SPECIAL_CHARS_ERROR,
)

from .models import QuestionList


class CreateQuestionListForm(forms.ModelForm):
    title = forms.CharField(
        label=_('Title'),
        help_text=MAX_AND_MIN_LENGTH,
        validators=[
            RegexValidator(r'^[0-9a-zA-Z ]*$', SPECIAL_CHARS_ERROR),
            MinLengthValidator(5),
        ],
    )
    captcha = ReCaptchaField()

    class Meta:
        model = QuestionList
        fields = ['title', 'tags']

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner')
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.owner = self.owner
        question_list = super().save(*args, **kwargs)
        return question_list


class CompleteListForm(forms.Form):
    custom_error_message = ''

    def __init__(self, *args, **kwargs):
        self.question_list = kwargs.pop('question_list')
        super().__init__(*args, **kwargs)

    def is_valid(self):
        if self.question_list.has_at_least_one_full_question():
            return True
        self.custom_error_message = LIST_COMPLETION_ERROR_MESSAGE
        return False

    def save(self, *args, **kwargs):
        self.question_list.activate()
        self.question_list.save()
        return self.question_list


class EditListForm(forms.ModelForm):
    title = forms.CharField(
        help_text=MAX_AND_MIN_LENGTH,
        validators=[
            RegexValidator(r'^[0-9a-zA-Z ]*$', SPECIAL_CHARS_ERROR),
            MinLengthValidator(5),
        ],
    )

    class Meta:
        model = QuestionList
        fields = ['title', 'tags']

    def save(self, *args, **kwargs):
        self.instance.slug = self.instance._generate_unique_slug_if_needed()
        question_list = super().save(*args, **kwargs)
        return question_list
