from django.test import TestCase
from django.urls import resolve, reverse

from lists.factories import QuestionListFactory

from core.mixins import TestViewsMixin
from ..factories import UserFactory
from ..views import UserListsView


class UserListsViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_and_login_a_user()
        self.base_url = reverse('lists', args=[self.user.username])

    def test_question_list_url_resolves_to_view(self):
        found = resolve('/users/javi/lists/')

        self.assertEqual(found.func.__name__, UserListsView.as_view().__name__)

    def test_returns_correct_html(self):
        response = self.client.get('/users/javi/lists/')

        self.assertTemplateUsed(response, 'user_lists.html')

    def test_contains_only_user_lists(self):
        user_2 = UserFactory(username='jorge')
        QuestionListFactory(title='list 1', owner=self.user)
        QuestionListFactory(title='list 2', owner=self.user)
        QuestionListFactory(title='list 3', owner=user_2)

        response_1 = self.client.get('/users/javi/lists/')
        html_1 = response_1.content.decode('utf-8')
        response_2 = self.client.get('/users/jorge/lists/')
        html_2 = response_2.content.decode('utf-8')

        self.assertRegex(html_1, 'list 1')
        self.assertRegex(html_1, 'list 2')
        self.assertNotRegex(html_1, 'list 3')
        self.assertRegex(html_2, 'list 3')
