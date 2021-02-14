import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.CustomUser'
        django_get_or_create = ('username',)

    username = 'testuser'
    email = 'testuser@email.com'
    password = 'hola1234'


class QuestionListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'questions.QuestionList'

    title = 'some title'
    owner = factory.SubFactory(UserFactory)


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'questions.Question'
        django_get_or_create = ('title',)

    title = 'Who is better?'
    child_of = factory.SubFactory(QuestionListFactory)


class AlternativeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'questions.Alternative'

    # alternative = 'Roger Federer'
    title = factory.Iterator(['Roger Federer', 'Rafael Nadal'])
    question = factory.SubFactory(QuestionFactory)
