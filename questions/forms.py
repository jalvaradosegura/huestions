from django import forms

from .constants import LIST_COMPLETION_ERROR_MESSAGE
from .factories import AlternativeFactory
from .models import Question, QuestionList


class AnswerQuestionForm(forms.Form):
    alternatives = forms.ChoiceField(
        label='Alternatives', widget=forms.RadioSelect
    )

    def __init__(self, question_id, *args, **kwargs):
        super().__init__(*args, **kwargs)

        question = Question.objects.get(id=question_id)

        self.fields['alternatives'].choices = [
            (x.id, x.title) for x in question.alternatives.all()
        ]


class CreateQuestionListForm(forms.ModelForm):
    class Meta:
        model = QuestionList
        fields = ['title']

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


class EditListForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.question_list = kwargs.pop('question_list')
        if 'new_data' in kwargs:
            new_data = kwargs.pop('new_data')
            self.new_title = new_data['list_title']
        super().__init__(*args, **kwargs)

        self.fields['list_title'] = forms.CharField(label='List title')

    def save(self):
        self.question_list.title = self.new_title
        self.question_list.save()


class CreateQuestionForm(forms.ModelForm):
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


class AddAlternativesForm(forms.Form):
    alternative_1 = forms.CharField()
    alternative_2 = forms.CharField()

    def __init__(self, *args, **kwargs):
        # self.question = kwargs.pop('question')
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        cleaned_data = super().clean()
        question = kwargs.pop('question')
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
        alternative = first_char_upper + alternative_1[1:]

        return alternative

    def clean_alternative_2(self):
        alternative_2 = self.cleaned_data['alternative_2']

        first_char = alternative_2[0]
        first_char_upper = first_char.upper()
        alternative = first_char_upper + alternative_2[1:]

        return alternative
