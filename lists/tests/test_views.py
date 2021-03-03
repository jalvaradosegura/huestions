from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse

from ..factories import QuestionListFactory
from ..models import QuestionList
from ..views import (
    create_list,
    DeleteListView,
    ListResultsView,
    QuestionsListView
)
from questions.constants import LIST_COMPLETION_ERROR_MESSAGE
from questions.factories import AlternativeFactory, QuestionFactory
from core.mixins import TestViewsMixin
from users.factories import UserFactory


class QuestionsListViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_and_login_a_user()
        self.base_url = reverse('questions_list')

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, QuestionsListView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, 'question_list.html')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class ListResultsViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_and_login_a_user()
        self.question_list = QuestionListFactory(title='an awesome list')
        self.base_url = reverse('list_results', args=[self.question_list.slug])

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'question_list_details_results.html')

    def test_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, ListResultsView.as_view().__name__
        )

    def test_page_contains_html(self):
        response = self.client.get(self.base_url)
        html = response.content.decode('utf8')

        self.assertRegex(
            html, f'These are the results for {self.question_list}!'
        )


class CreateListViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_and_login_a_user()
        self.base_url = reverse('create_list')

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'create_question_list.html')

    def test_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(found.func.__name__, create_list.__name__)

    def test_page_contains_title_within_html(self):
        response = self.client.get(self.base_url)

        self.assertContains(response, 'Create a question')

    def test_page_contains_form_within_html(self):
        response = self.client.get(self.base_url)
        html = response.content.decode('utf8')

        self.assertRegex(html, '<form.*>')
        self.assertRegex(html, '</form>')

    def test_post_success(self):
        response = self.client.post(
            self.base_url, data={'title': 'super list'}
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('add_question', kwargs={'list_slug': 'super-list'})
        )


class EditListViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_and_login_a_user()
        self.question_list = QuestionListFactory(
            title='awesome list', owner=self.user
        )
        self.base_url = reverse('edit_list', args=[self.question_list.slug])
        question = QuestionFactory(title='cool?', child_of=self.question_list)
        AlternativeFactory(title='yes', question=question)
        AlternativeFactory(title='no', question=question)

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'edit_question_list.html')

    def test_cant_access_if_user_is_not_the_owner(self):
        user_1 = UserFactory(username='Jorge', email='jorge@email.com')
        question_list = QuestionListFactory(title='access list', owner=user_1)

        response = self.client.get(
            reverse('edit_list', kwargs={'slug': question_list.slug})
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_cant_access_if_list_is_already_published(self):
        question_list = QuestionListFactory(
            title='access list', owner=self.user, active=True
        )

        response = self.client.get(
            reverse('edit_list', kwargs={'slug': question_list.slug})
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_post_change_name_success(self):
        response = self.client.post(
            self.base_url,
            data={'title': 'another title'}
        )
        question_list = QuestionList.objects.last()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('lists', kwargs={'username': self.user.username})
        )
        self.assertEqual(question_list.slug, 'another-title')

    def test_post_publish_list_success(self):
        response = self.client.post(self.base_url, data={})
        modified_list = QuestionList.objects.get(slug=self.question_list.slug)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(self.question_list.active)
        self.assertTrue(modified_list.active)

    def test_post_publish_list_fail(self):
        question_list = QuestionListFactory(title='cool list', owner=self.user)

        response = self.client.post(
            reverse('edit_list', kwargs={'slug': question_list.slug}),
            data={}
        )
        request = response.wsgi_request
        storage = get_messages(request)
        messages = [message.message for message in storage]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(LIST_COMPLETION_ERROR_MESSAGE, messages)


class DeleteListViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_and_login_a_user()
        self.question_list = QuestionListFactory(
            title='test error list', owner=self.user
        )
        self.base_url = reverse(
            'delete_list', kwargs={'slug': self.question_list.slug}
        )

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, DeleteListView.as_view().__name__
        )

    def test_cant_access_if_user_is_not_the_owner(self):
        user_1 = UserFactory(username='Jorge', email='jorge@email.com')
        question_list = QuestionListFactory(title='access list', owner=user_1)

        response = self.client.get(
            reverse('delete_list', kwargs={'slug': question_list.slug})
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_cant_access_if_list_is_already_published(self):
        self.question_list.activate()
        self.question_list.save()

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_post_success(self):
        response = self.client.post(self.base_url, data={})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('lists', kwargs={'username': self.user.username})
        )
