from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve, reverse

from ..constants import (
    ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE,
    LIST_COMPLETION_ERROR_MESSAGE,
)
from ..factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
)
from ..forms import AddAlternativesForm
from ..models import Alternative, Question
from ..views import (
    AnswerListView,
    home,
    DeleteQuestionView,
)
from .mixins import ViewsMixin
from lists.models import QuestionList
from lists.views import (
    create_list,
    DeleteListView,
    ListResultsView,
    QuestionsListView,
)
from users.factories import UserFactory
from votes.models import Vote


class HomePageViewTests(ViewsMixin, TestCase):
    base_url = reverse('home')

    def setUp(self):
        self.create_and_login_a_user()

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve(self.base_url)

        self.assertEqual(found.func, home)

    def test_root_url_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'home.html')


class SignUpPageTests(TestCase):
    def test_signup_url_returns_correct_html(self):
        response = self.client.get(reverse('account_signup'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'account/signup.html')


class LoginPageTests(TestCase):
    def test_login_url_returns_correct_html(self):
        response = self.client.get(reverse('account_login'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'account/login.html')


class LogoutPageTests(ViewsMixin, TestCase):
    base_url = reverse('account_logout')

    def test_logout_url_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'account/logout.html')


class QuestionsListViewTests(ViewsMixin, TestCase):
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


class AnswerListViewTests(ViewsMixin, TestCase):
    def setUp(self):
        self.create_and_login_a_user()
        self.question_list = QuestionListFactory(
            title='base list', owner=self.user
        )
        self.base_url = reverse('answer_list', args=[self.question_list.slug])
        question = QuestionFactory(
            title='base question', child_of=self.question_list
        )
        AlternativeFactory(
            title='base alternative 1', question=question
        ).users.add(self.user)
        AlternativeFactory(title='base alternative 2', question=question)

    def test_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AnswerListView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'question_list_details.html')

    def test_pagination_works(self):
        QuestionFactory(title='some question', child_of=self.question_list)
        QuestionFactory(title='another question', child_of=self.question_list)

        response = self.client.get(self.base_url + '?page=1')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'question_list_details.html')

    def test_message_that_you_already_answered_the_question(self):
        response = self.client.get(self.base_url + '?page=1')
        html = response.content.decode('utf8')

        self.assertRegex(
            html, "Question already answered. Your vote won't count this time."
        )

    def test_no_message_that_you_already_answered_the_question(self):
        question_list = QuestionListFactory(title='no message')
        question = QuestionFactory(
            title='some question', child_of=question_list
        )
        AlternativeFactory(question=question)

        response = self.client.get(
            reverse('answer_list', args=[question_list.slug]) + '?page=1'
        )
        html = response.content.decode('utf8')

        self.assertNotRegex(
            html, "Question already answered. Your vote won't count this time."
        )

    def test_attempt_to_access_an_incomplete_list(self):
        question_list = QuestionListFactory(title='cool list')

        response = self.client.get(
            reverse('answer_list', kwargs={'slug': question_list.slug})
            + '?page=1'
        )
        request = response.wsgi_request
        storage = get_messages(request)
        message = [message.message for message in storage][0]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(message, ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE)

    def test_post_success(self):
        question_list = QuestionListFactory(title='post list', owner=self.user)
        question = QuestionFactory(
            title='post question', child_of=question_list
        )
        AlternativeFactory(title='post alternative 1', question=question)
        AlternativeFactory(title='post alternative 2', question=question)

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug]),
            data={
                'alternatives': '3',
                'question_list_id': question_list.id,
                'next_page': '2',
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_list', args=[question_list.slug]) + '?page=2'
        )
        self.assertEqual(Vote.objects.last().list.__str__(), 'post list')


class ListResultsViewTests(ViewsMixin, TestCase):
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


class CreateListViewTests(ViewsMixin, TestCase):
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


class EditListViewTests(ViewsMixin, TestCase):
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


class AddQuestionViewTests(ViewsMixin, TestCase):
    def setUp(self):
        self.create_and_login_a_user()
        self.question_list = QuestionListFactory(
            title='An amazing list', owner=self.user
        )
        self.base_url = reverse('add_question', args=[self.question_list.slug])

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'create_question.html')

    def test_post_complete_list_fail(self):
        response = self.client.post(self.base_url, data={})
        question_list = QuestionList.objects.get(id=self.question_list.id)
        request = response.wsgi_request
        storage = get_messages(request)
        message = [message.message for message in storage][0]

        self.assertFalse(question_list.active)
        self.assertEqual(message, LIST_COMPLETION_ERROR_MESSAGE)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_complete_list_success(self):
        question = QuestionFactory(title='cool?', child_of=self.question_list)
        AlternativeFactory(title='yes', question=question)
        AlternativeFactory(title='no', question=question)

        response = self.client.post(self.base_url, data={})
        modified_list = QuestionList.objects.get(id=self.question_list.id)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(self.question_list.active)
        self.assertTrue(modified_list.active)

    def test_post_create_question_success(self):
        response = self.client.post(
            self.base_url,
            data={
                'title': 'Is this hard to answer?',
                'alternative_1': 'Yes',
                'alternative_2': 'No',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('add_question', args=[self.question_list.slug]),
        )

    def test_cant_access_if_user_is_not_the_owner(self):
        user_1 = UserFactory(username='Jorge', email='jorge@email.com')
        question_list = QuestionListFactory(title='access list', owner=user_1)

        response = self.client.get(
            reverse('add_question', kwargs={'list_slug': question_list.slug})
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_cant_access_if_list_is_already_published(self):
        question_list = QuestionListFactory(
            title='a list', owner=self.user, active=True
        )

        response = self.client.get(
            reverse('add_question', kwargs={'list_slug': question_list.slug})
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class EditQuestionViewTests(ViewsMixin, TestCase):
    def setUp(self):
        self.create_and_login_a_user()
        self.question_list = QuestionListFactory(
            title='An amazing list', owner=self.user
        )
        self.question = QuestionFactory(
            title='what?', child_of=self.question_list
        )
        self.alternative_1 = AlternativeFactory(
            title='Yes it is', question=self.question
        )
        self.alternative_2 = AlternativeFactory(
            title="No it isn't", question=self.question
        )
        self.base_url = reverse(
            'edit_question',
            kwargs={
                'list_slug': self.question_list.slug,
                'slug': self.question.slug,
                'question_id': self.question.id
            }
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'edit_question.html')

    def test_cant_access_if_user_is_not_the_owner(self):
        user_1 = UserFactory(username='Jorge', email='jorge@email.com')
        question_list = QuestionListFactory(title='access list', owner=user_1)
        question = QuestionFactory(title='what?', child_of=question_list)
        AlternativeFactory(title='Yes it is', question=question)
        AlternativeFactory(title="No it isn't", question=question)

        response = self.client.get(
            reverse(
                'edit_question',
                kwargs={
                    'list_slug': question_list.slug,
                    'slug': question.slug,
                    'question_id': question.id
                }
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_cant_access_if_list_is_already_published(self):
        self.question_list.active = True
        self.question_list.save()

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_pass_alternatives_form_to_context(self):
        response = self.client.get(self.base_url)

        self.assertIsInstance(
            response.context['alternatives_form'], AddAlternativesForm
        )

    def test_forms_are_being_used_within_template(self):
        response = self.client.get(self.base_url)
        html = response.content.decode('utf8')

        self.assertRegex(html, '<label for="id_title">')
        self.assertRegex(html, '<label for="id_alternative_1">')
        self.assertRegex(html, '<label for="id_alternative_2">')

    def test_post_success(self):
        response = self.client.post(
            self.base_url,
            data={
                'title': 'edited',
                'alternative_1': 'edited',
                'alternative_2': 'edited',
            },
        )
        edited_question = Question.objects.get(id=self.question.id)
        edited_alternative_1 = Alternative.objects.get(
            id=self.alternative_1.id
        )
        edited_alternative_2 = Alternative.objects.get(
            id=self.alternative_2.id
        )

        self.assertEqual(edited_question.title, 'edited')
        self.assertEqual(edited_alternative_1.title, 'Edited')
        self.assertEqual(edited_alternative_2.title, 'Edited')
        self.assertEqual(
            response['Location'],
            reverse('edit_list', kwargs={'slug': self.question_list.slug})
        )


class DeleteListViewTests(ViewsMixin, TestCase):
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


class DeleteQuestionViewTests(ViewsMixin, TestCase):
    def setUp(self):
        self.create_and_login_a_user()
        self.question_list = QuestionListFactory(
            title='test error list', owner=self.user
        )
        question = QuestionFactory(title='cool?', child_of=self.question_list)
        self.base_url = reverse(
            'delete_question',
            kwargs={'slug': self.question_list.slug, 'id': question.id}
        )

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, DeleteQuestionView.as_view().__name__
        )

    def test_post_success(self):
        response = self.client.post(self.base_url, data={})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('edit_list', kwargs={'slug': self.question_list.slug})
        )
