from http import HTTPStatus
from unittest.mock import patch

from django.contrib.messages import get_messages
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import resolve, reverse

from ..constants import INVALID_HEADER_ON_EMAIL
from ..views import (
    AboutView,
    ContactSuccessView,
    ContactView,
    CookiePolicyView,
    HiddenRedPandaView,
    TermsAndConditionsView,
    handler403,
    handler404,
    handler500,
)


class TermsAndConditionsViewTests(TestCase):
    def setUp(self):
        self.base_url = reverse('terms_and_conditions')

    def test_url_resolves_to_view(self):
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

    def test_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(found.func.__name__, AboutView.as_view().__name__)

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, AboutView.template_name)


class ContactViewTests(TestCase):
    def setUp(self):
        self.base_url = reverse('contact')

    def test_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(found.func.__name__, ContactView.as_view().__name__)

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, ContactView.template_name)

    def test_post_success(self):
        response = self.client.post(
            self.base_url,
            data={
                'from_email': 'test@email.com',
                'subject': 'test',
                'message': 'awesome',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response['Location'], reverse('contact_success'))

    def test_post_fail_invalid_email(self):
        response = self.client.post(
            self.base_url,
            data={
                'from_email': 'testemail.com',
                'subject': 'test',
                'message': 'awesome',
            },
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
                'message': 'awesome',
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

    def test_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, ContactSuccessView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, ContactSuccessView.template_name)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class Handler500ViewTests(TestCase):
    def test_response(self):
        response = HttpResponse(status=500)

        self.assertEqual(
            response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR
        )

    def test_call_handler_directly(self):
        factory = RequestFactory()
        request = factory.get('/')
        response = handler500(request)
        self.assertEqual(response.status_code, 500)


class Error500ViewTests(TestCase):
    def test_returns_correct_html(self):
        response = self.client.get(reverse('500'))

        self.assertTemplateUsed(response, 'errors/500.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class Handler403ViewTests(TestCase):
    def test_response(self):
        response = HttpResponse(status=403)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_call_handler_directly(self):
        factory = RequestFactory()
        request = factory.get('/')
        response = handler403(request)
        self.assertEqual(response.status_code, 403)


class Error403ViewTests(TestCase):
    def test_returns_correct_html(self):
        response = self.client.get(reverse('403'))

        self.assertTemplateUsed(response, 'errors/403.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class Handler404ViewTests(TestCase):
    def test_response(self):
        response = HttpResponse(status=404)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_visit_url_that_does_not_exist(self):
        response = self.client.get('this-url-will-never-exist')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_call_handler_directly(self):
        factory = RequestFactory()
        request = factory.get('/')
        response = handler404(request)
        self.assertEqual(response.status_code, 404)


class Error404ViewTests(TestCase):
    def test_returns_correct_html(self):
        response = self.client.get(reverse('404'))

        self.assertTemplateUsed(response, 'errors/404.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class HiddenRedPandaViewTests(TestCase):
    def setUp(self):
        self.base_url = reverse('hidden_red_panda')

    def test_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, HiddenRedPandaView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, 'hidden_red_panda.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class CookiePolicyViewTests(TestCase):
    def setUp(self):
        self.base_url = reverse('cookies_policy')

    def test_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, CookiePolicyView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, 'cookies_policy.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)
