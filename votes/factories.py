import factory

from questions.factories import (
    QuestionListFactory,
    QuestionFactory,
    AlternativeFactory,
)
from users.factories import UserFactory


class VoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'votes.Vote'

    user = factory.SubFactory(UserFactory)
    list = factory.SubFactory(QuestionListFactory)
    question = factory.SubFactory(QuestionFactory)
    alternative = factory.SubFactory(AlternativeFactory)
