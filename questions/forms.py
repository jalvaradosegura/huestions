from django import forms
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
)
from django.utils.translation import gettext_lazy as _

from core.constants import (
    AMOUNT_OF_QUESTIONS_PER_LIST,
    FILE_TOO_LARGE_HELPER,
    HUESTIONS_REGEX,
    LIST_REACHED_MAXIMUM_OF_QUESTION,
    MAX_AND_MIN_LENGTH,
    MAX_AND_SPECIAL_CHARS,
    MAX_AND_SPECIAL_CHARS_ATTRIBUTIONS,
    SPECIAL_CHARS_ERROR,
)

from .models import Alternative, Question
from .validators import file_extension_validator, file_size_validator


class AnswerQuestionForm(forms.Form):
    alternatives = forms.ChoiceField(
        label=_('Alternatives'), widget=forms.RadioSelect
    )

    def __init__(self, question_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        question = Question.objects.get(id=question_id)
        alternative_1, alternative_2 = question.alternatives.all()

        self.fields['alternatives'].choices = [
            (alternative_1.id, alternative_1.title),
            (alternative_2.id, alternative_2.title),
        ]

        self.img_1_url = alternative_1.image.url
        self.img_2_url = alternative_2.image.url

        self.attribution_1 = alternative_1.attribution
        self.attribution_2 = alternative_2.attribution


class CreateQuestionForm(forms.ModelForm):
    title = forms.CharField(
        label=_('Title'),
        help_text=MAX_AND_MIN_LENGTH,
        validators=[
            RegexValidator(HUESTIONS_REGEX, SPECIAL_CHARS_ERROR),
            MinLengthValidator(5),
        ],
    )
    questions_amount_limit = AMOUNT_OF_QUESTIONS_PER_LIST

    class Meta:
        model = Question
        fields = ['title']

    def __init__(self, *args, **kwargs):
        self.question_list = kwargs.pop('question_list')
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.child_of = self.question_list
        question = super(CreateQuestionForm, self).save(*args, **kwargs)
        return question

    def clean(self):
        if self.question_list.questions.count() >= self.questions_amount_limit:
            raise forms.ValidationError(LIST_REACHED_MAXIMUM_OF_QUESTION)


class AddAlternativesForm(forms.Form):
    image_1 = forms.ImageField(
        required=False,
        validators=[file_size_validator, file_extension_validator],
        help_text=FILE_TOO_LARGE_HELPER,
    )
    alternative_1 = forms.CharField(
        label=_('Alternative 1'),
        help_text=MAX_AND_SPECIAL_CHARS,
        validators=[
            RegexValidator(HUESTIONS_REGEX, SPECIAL_CHARS_ERROR),
            MaxLengthValidator(limit_value=100),
        ],
    )
    attribution_1 = forms.CharField(
        label=_('(Optional) Credit for the image 1'),
        widget=forms.Textarea,
        help_text=MAX_AND_SPECIAL_CHARS_ATTRIBUTIONS,
        validators=[
            MaxLengthValidator(limit_value=200),
        ],
        required=False,
    )
    image_2 = forms.ImageField(
        required=False,
        validators=[file_size_validator],
        help_text=FILE_TOO_LARGE_HELPER,
    )
    alternative_2 = forms.CharField(
        label=_('Alternative 2'),
        help_text=MAX_AND_SPECIAL_CHARS,
        validators=[
            RegexValidator(HUESTIONS_REGEX, SPECIAL_CHARS_ERROR),
            MaxLengthValidator(limit_value=100),
        ],
    )
    attribution_2 = forms.CharField(
        label=_('(Optional) Credit for the image 2'),
        widget=forms.Textarea,
        help_text=MAX_AND_SPECIAL_CHARS_ATTRIBUTIONS,
        validators=[
            MaxLengthValidator(limit_value=200),
        ],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        cleaned_data = super().clean()
        question = kwargs.pop('question')

        if question.alternatives.exists():
            alternative_1 = question.alternatives.first()
            alternative_2 = question.alternatives.last()
            alternative_1.title = cleaned_data.get('alternative_1')
            alternative_2.title = cleaned_data.get('alternative_2')

            Alternative.objects.bulk_update(
                [alternative_1, alternative_2], ['title']
            )
        else:
            if cleaned_data.get('image_1'):
                alternative_1 = Alternative.objects.create(
                    title=cleaned_data.get('alternative_1'),
                    image=cleaned_data.get('image_1'),
                    question=question,
                    attribution=cleaned_data.get('attribution_1'),
                )
            else:
                alternative_1 = Alternative.objects.create(
                    title=cleaned_data.get('alternative_1'),
                    question=question,
                    attribution=cleaned_data.get('attribution_1'),
                )

            if cleaned_data.get('image_2'):
                alternative_2 = Alternative.objects.create(
                    title=cleaned_data.get('alternative_2'),
                    image=cleaned_data.get('image_2'),
                    question=question,
                    attribution=cleaned_data.get('attribution_2'),
                )
            else:
                alternative_2 = Alternative.objects.create(
                    title=cleaned_data.get('alternative_2'),
                    question=question,
                    attribution=cleaned_data.get('attribution_2'),
                )

    def clean_alternative_1(self):
        alternative_1 = self.cleaned_data['alternative_1']

        first_char = alternative_1[0]
        first_char_upper = first_char.upper()

        return first_char_upper + alternative_1[1:]

    def clean_alternative_2(self):
        alternative_2 = self.cleaned_data['alternative_2']

        first_char = alternative_2[0]
        first_char_upper = first_char.upper()

        return first_char_upper + alternative_2[1:]
