from http import HTTPStatus
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse

from ..constants import INVALID_HEADER_ON_EMAIL
from ..views import (
    AboutView,
    ContactView,
    ContactSuccessView,
    TermsAndConditionsView
)


class TermsAndConditionsViewTests(TestCase):
    def setUp(self):
        self.base_url = reverse('terms_and_conditions')

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, TermsAndConditionsView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, TermsAndConditionsView.template_name)


class AboutViewTests(TestCase):
    def setUp(self):
        self.base_url = reverse('about')

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AboutView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, AboutView.template_name)


class ContactViewTests(TestCase):
    def setUp(self):
        self.base_url = reverse('contact')

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, ContactView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, ContactView.template_name)

    def test_post_success(self):
        response = self.client.post(
            self.base_url,
            data={
                'from_email': 'test@email.com',
                'subject': 'test',
                'message': 'awesome'
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response['Location'], reverse('contact_success'))

    def test_post_fail_invalid_email(self):
        response = self.client.post(
            self.base_url,
            data={
                'from_email': 'testemail.com',
                'subject': 'test',
                'message': 'awesome'
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, ContactView.template_name)

    @patch('core.views.FOR_TESTING')
    def test_post_fail_invalid_header(self, mock):
        mock.return_value = True
        response = self.client.post(
            self.base_url,
            data={
                'from_email': 'test@email.com',
                'subject': 'test',
                'message': 'awesome'
            },
        )
        request = response.wsgi_request
        storage = get_messages(request)
        messages = [message.message for message in storage]

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, ContactView.template_name)
        self.assertIn(INVALID_HEADER_ON_EMAIL, messages)


class ContactSuccessViewTests(TestCase):
    def setUp(self):
        self.base_url = reverse('contact_success')

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, ContactSuccessView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, ContactSuccessView.template_name)
