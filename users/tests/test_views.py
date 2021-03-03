from django.test import TestCase
from django.urls import resolve

from lists.factories import QuestionListFactory
from ..factories import UserFactory
from ..views import UserListsView


class UserListsViewTests(TestCase):
    def test_question_list_url_resolves_to_view(self):

        found = resolve('/users/javi/lists/')
        self.assertEqual(found.func.__name__, UserListsView.as_view().__name__)

    def test_returns_correct_html(self):
        UserFactory(username='javi')
        response = self.client.get('/users/javi/lists/')

        self.assertTemplateUsed(response, 'user_lists.html')

    def test_contains_only_user_lists(self):
        user_1 = UserFactory(username='javi')
        user_2 = UserFactory(username='jorge')
        QuestionListFactory(title='list 1', owner=user_1)
        QuestionListFactory(title='list 2', owner=user_1)
        QuestionListFactory(title='list 3', owner=user_2)

        response_1 = self.client.get('/users/javi/lists/')
        html_1 = response_1.content.decode('utf-8')
        response_2 = self.client.get('/users/jorge/lists/')
        html_2 = response_2.content.decode('utf-8')

        self.assertRegex(html_1, 'list 1')
        self.assertRegex(html_1, 'list 2')
        self.assertNotRegex(html_1, 'list 3')
        self.assertRegex(html_2, 'list 3')
