from django.test import TestCase

from questions.factory import UserFactory


class LoginTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_login(self):
        self.client.force_login(self.user)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_not_authorized_to_see_the_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
