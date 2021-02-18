from django.test import TestCase
from django.urls import resolve

from .views import UserListsView


class QuestionsListViewTests(TestCase):
    def test_question_list_url_resolves_to_view(self):

        found = resolve('/users/javi/lists/')
        self.assertEqual(
            found.func.__name__, UserListsView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get('/users/javi/lists/')

        self.assertTemplateUsed(response, 'user_lists.html')
