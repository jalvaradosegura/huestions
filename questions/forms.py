from django import forms
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    RegexValidator,
)
from django.utils.translation import gettext_lazy as _

from core.constants import (
    LIST_REACHED_MAXIMUM_OF_QUESTION,
    SPECIAL_CHARS_ERROR,
)

from .factories import AlternativeFactory
from .models import Question


class AnswerQuestionForm(forms.Form):
    alternatives = forms.ChoiceField(
        label=_('Alternatives'), widget=forms.RadioSelect
    )

    def __init__(self, question_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        question = Question.objects.get(id=question_id)

        self.fields['alternatives'].choices = [
            (x.id, x.title) for x in question.alternatives.all()
        ]


class CreateQuestionForm(forms.ModelForm):
    title = forms.CharField(
        validators=[
            RegexValidator(r'^[0-9a-zA-Z\\? ]*$', SPECIAL_CHARS_ERROR),
            MinLengthValidator(5),
        ]
    )
    questions_amount_limit = 20

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

    def clean_title(self):
        title = self.cleaned_data['title']

        title_question_marks_removed = title.replace('?', '')
        title_question_mark_appended = title_question_marks_removed + '?'

        return title_question_mark_appended

    def clean(self):
        if self.question_list.questions.count() >= self.questions_amount_limit:
            raise forms.ValidationError(LIST_REACHED_MAXIMUM_OF_QUESTION)


class AddAlternativesForm(forms.Form):
    alternative_1 = forms.CharField(
        label=_('Alternative 1'),
        validators=[
            RegexValidator(r'^[0-9a-zA-Z ]*$', SPECIAL_CHARS_ERROR),
            MaxLengthValidator(limit_value=100),
        ],
    )
    alternative_2 = forms.CharField(
        label=_('Alternative 2'),
        validators=[
            RegexValidator(r'^[0-9a-zA-Z ]*$', SPECIAL_CHARS_ERROR),
            MaxLengthValidator(limit_value=100),
        ],
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

            alternative_1.save()
            alternative_2.save()
        else:
            AlternativeFactory(
                title=cleaned_data.get('alternative_1'), question=question
            )
            AlternativeFactory(
                title=cleaned_data.get('alternative_2'), question=question
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
