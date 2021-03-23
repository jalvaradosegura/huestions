from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..forms import MyCustomSignupForm


class CreateQuestionFormTests(TestCase):
    def test_valid_form(self):
        form = MyCustomSignupForm(
            data={
                'email': 'someemail@email.com',
                'password1': 'Hello12345678',
                'check': True,
            }
        )
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        form = MyCustomSignupForm(
            data={
                'email': 'someemail@email.com',
                'password1': 'Hello12345678',
                'check': False,
            }
        )
        self.assertFalse(form.is_valid())

    def test_create_user_post(self):
        response = self.client.post(
            reverse('account_signup'),
            data={
                'email': 'someemail@email.com',
                'password1': 'Hello12345678',
                'check': True,
            },
        )
        new_user = get_user_model().objects.last()

        self.assertEqual(new_user.username, 'someemail')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
