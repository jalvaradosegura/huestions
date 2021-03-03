import factory

from users.factories import UserFactory


class QuestionListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'lists.QuestionList'

    title = 'some title'
    owner = factory.SubFactory(UserFactory)
