import factory


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'questions.Question'
        django_get_or_create = ('question',)

    question = 'Who is better?'


class AlternativeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'questions.Alternative'

    # alternative = 'Roger Federer'
    alternative = factory.Iterator(['Roger Federer', 'Rafael Nadal'])
    question = factory.SubFactory(QuestionFactory)
