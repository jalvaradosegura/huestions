from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse

from core.constants import (
    LIST_COMPLETION_ERROR_MESSAGE,
    MUST_COMPLETE_LIST_BEFORE_SEING_RESULTS,
)
from core.mixins import TestViewsMixin
from questions.factories import AlternativeFactory, QuestionFactory
from users.factories import UserFactory

from ..factories import QuestionListFactory
from ..models import QuestionList
from ..views import (
    DeleteListView,
    EditListView,
    ListResultsView,
    QuestionsListView,
    create_list,
)


class QuestionsListViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_login_and_verify_user()
        self.base_url = reverse('questions_list')

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, QuestionsListView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, QuestionsListView.template_name)
        self.assertEqual(response.status_code, HTTPStatus.OK)


class ListResultsViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_login_and_verify_user()
        self.question_list = QuestionListFactory(title='an awesome list')
        self.base_url = reverse('list_results', args=[self.question_list.slug])

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, ListResultsView.template_name)

    def test_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, ListResultsView.as_view().__name__
        )

    def test_redirect_if_user_havent_completed_the_list(self):
        question_list = QuestionListFactory(title="user won't do this list")
        QuestionFactory(child_of=question_list)

        response = self.client.get(
            reverse('list_results', args=[question_list.slug])
        )
        request = response.wsgi_request
        storage = get_messages(request)
        messages = [message.message for message in storage]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_list', args=[question_list.slug]),
        )
        self.assertIn(MUST_COMPLETE_LIST_BEFORE_SEING_RESULTS, messages)

    def test_dont_redirect_if_user_have_completed_the_list(self):
        question_list = QuestionListFactory(title="user won't do this list")
        question = QuestionFactory(child_of=question_list)
        alternative = AlternativeFactory(question=question)
        alternative.vote_for_this_alternative(self.user)

        response = self.client.get(
            reverse('list_results', args=[question_list.slug])
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, ListResultsView.template_name)

    def test_redirect_with_invitation_if_user_havent_completed_the_list(self):
        user = UserFactory()
        question_list = QuestionListFactory(title="user won't do this list")
        QuestionFactory(child_of=question_list)

        response = self.client.get(
            reverse('list_results', args=[question_list.slug, user])
        )
        request = response.wsgi_request
        storage = get_messages(request)
        messages = [message.message for message in storage]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_list', args=[question_list.slug, user]),
        )
        self.assertIn(MUST_COMPLETE_LIST_BEFORE_SEING_RESULTS, messages)


class CreateListViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_login_and_verify_user()
        self.base_url = reverse('create_list')

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'create_list.html')

    def test_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(found.func.__name__, create_list.__name__)

    def test_page_contains_title_within_html(self):
        response = self.client.get(self.base_url)

        self.assertContains(response, 'Create a list')

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
            reverse('add_question', kwargs={'list_slug': 'super-list'}),
        )

    def test_post_fail(self):
        response = self.client.post(
            self.base_url, data={'title': '-' * 101}
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'create_list.html')


class EditListViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_login_and_verify_user()
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
        self.assertTemplateUsed(response, EditListView.template_name)

    def test_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(found.func.__name__, EditListView.__name__)

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
            self.base_url, data={'title': 'another title'}
        )
        question_list = QuestionList.objects.last()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('lists', kwargs={'username': self.user.username}),
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
            reverse('edit_list', kwargs={'slug': question_list.slug}), data={}
        )
        request = response.wsgi_request
        storage = get_messages(request)
        messages = [message.message for message in storage]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(LIST_COMPLETION_ERROR_MESSAGE, messages)


class DeleteListViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_login_and_verify_user()
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

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, DeleteListView.template_name)

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
            reverse('lists', kwargs={'username': self.user.username}),
        )
