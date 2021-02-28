from django.test import TestCase
from django.contrib.auth import get_user_model

from ..factories import UserFactory


class UserFactoryTests(TestCase):
    def setUp(self):
        UserFactory()

    def test_user_got_created(self):
        user = get_user_model().objects.last()

        self.assertEqual(user.username, 'testuser')
