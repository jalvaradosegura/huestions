from django import forms

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


class CreateQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title']
