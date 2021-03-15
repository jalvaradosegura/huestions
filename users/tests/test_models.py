from django.test import TestCase

from lists.factories import QuestionListFactory
from ..factories import UserFactory


class CustomUserModelTests(TestCase):
    def test_get_amount_of_lists_created(self):
        user = UserFactory(username='random')
        QuestionListFactory(owner=user)
        QuestionListFactory(owner=user)
        QuestionListFactory(owner=user)

        self.assertEqual(user.get_amount_of_lists_created(), 3)
