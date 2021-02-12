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

    def __init__(self, *args, **kwargs):
        self.question_list = kwargs.pop('question_list')
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.child_of = self.question_list
        question = super(CreateQuestionForm, self).save(*args, **kwargs)
        return question


class AddAlternativesForm(forms.Form):
    alternative_1 = forms.CharField()
    alternative_2 = forms.CharField()
