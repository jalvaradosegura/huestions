from django.test import TestCase
from django.urls import resolve, reverse

from ..views import AboutView, TermsAndConditionsView


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
