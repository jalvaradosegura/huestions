from http import HTTPStatus

from django.test import TestCase
from django.urls import resolve, reverse

from core.mixins import DeleteTestImagesOfAlternativesMixin, TestViewsMixin
from lists.factories import QuestionListFactory
from questions.factories import AlternativeFactory

from ..factories import UserFactory
from ..views import UserListsView, UserStatsView


class UserListsViewTests(
    DeleteTestImagesOfAlternativesMixin, TestViewsMixin, TestCase
):
    def setUp(self):
        self.create_login_and_verify_user()
        self.base_url = reverse('lists', args=[self.user.username])

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(found.func.__name__, UserListsView.as_view().__name__)

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, 'user_lists.html')

    def test_contains_only_user_lists(self):
        user_2 = UserFactory(username='jorge')
        QuestionListFactory(title='list 1', owner=self.user)
        QuestionListFactory(title='list 2', owner=self.user)
        QuestionListFactory(title='list 3', owner=user_2)

        response_1 = self.client.get(self.base_url)
        html_1 = response_1.content.decode('utf-8')
        response_2 = self.client.get(reverse('lists', args=[user_2.username]))
        html_2 = response_2.content.decode('utf-8')

        self.assertRegex(html_1, 'list 1')
        self.assertRegex(html_1, 'list 2')
        self.assertNotRegex(html_1, 'list 3')
        self.assertRegex(html_2, 'list 3')

    def test_filter_parameters_published(self):
        question_list_1 = QuestionListFactory(
            title='published list', owner=self.user, active=True
        )
        question_list_2 = QuestionListFactory(
            title='not published', owner=self.user
        )

        response = self.client.get(self.base_url + '?filter=published')
        html = response.content.decode('utf-8')

        self.assertRegex(html, question_list_1.title)
        self.assertNotRegex(html, question_list_2.title)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_filter_parameters_unpublished(self):
        question_list_1 = QuestionListFactory(
            title='published list', owner=self.user, active=True
        )
        question_list_2 = QuestionListFactory(
            title='not published', owner=self.user
        )

        response = self.client.get(self.base_url + '?filter=unpublished')
        html = response.content.decode('utf-8')

        self.assertRegex(html, question_list_2.title)
        self.assertNotRegex(html, question_list_1.title)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class UserStatsViewTests(
    DeleteTestImagesOfAlternativesMixin, TestViewsMixin, TestCase
):
    def setUp(self):
        self.create_login_and_verify_user()
        self.base_url = reverse('stats', args=[self.user.username])

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(found.func.__name__, UserStatsView.as_view().__name__)

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, 'user_stats.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_html_contains_amount_of_lists_created(self):
        QuestionListFactory(owner=self.user)
        QuestionListFactory(owner=self.user)
        QuestionListFactory(owner=self.user)

        response = self.client.get(self.base_url)
        html = response.content.decode('utf8')

        self.assertRegex(html, '3')

    def test_html_contains_amount_of_questions_answered(self):
        for i in range(10):
            AlternativeFactory().vote_for_this_alternative(self.user)

        response = self.client.get(self.base_url)
        html = response.content.decode('utf8')

        self.assertRegex(html, '10')

    def test_cant_access_if_user_is_not_the_owner_of_the_stats_profile(self):
        user = UserFactory(username='jorge', email='jorge@email.com')

        response = self.client.get(reverse('stats', args=[user.username]))

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
