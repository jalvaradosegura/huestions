import factory


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'questions.Question'
        django_get_or_create = ('question',)

    question = 'Who is better?'
