import factory

from lists.factories import QuestionListFactory


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'questions.Question'

    title = 'Who is better?'
    child_of = factory.SubFactory(QuestionListFactory)


class AlternativeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'questions.Alternative'

    title = factory.Iterator(['Roger Federer', 'Rafael Nadal'])
    question = factory.SubFactory(QuestionFactory)
    image = factory.django.ImageField(color='blue')
