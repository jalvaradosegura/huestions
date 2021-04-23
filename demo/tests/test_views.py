from django.test import TestCase
from django.urls import resolve, reverse

from ..views import DemoHomeView


class DemoHomeViewTests(TestCase):
    def setUp(self):
        self.base_url = reverse('demo_home')

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, DemoHomeView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, DemoHomeView.template_name)
