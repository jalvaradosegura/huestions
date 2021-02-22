from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve

from ..constants import (
    ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE,
    LIST_COMPLETION_ERROR_MESSAGE
)
from ..factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
    UserFactory
)
from .mixins import ViewsMixin
from ..models import QuestionList
from ..views import (
    AnswerQuestionListView,
    QuestionsListView,
    QuestionListResultsView,
    home,
    create_question_list
)


class HomePageTests(ViewsMixin, TestCase):
    base_url = '/'

    def test_root_url_resolves_to_home_page_view(self):
        self.create_and_login_a_user()

        found = resolve('/')

        self.assertEqual(found.func, home)

    def test_root_url_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get('/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'home.html')


class SignUpPageTests(TestCase):
    def test_signup_url_returns_correct_html(self):
        response = self.client.get('/accounts/signup/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'account/signup.html')


class LoginPageTests(TestCase):
    def test_login_url_returns_correct_html(self):
        response = self.client.get('/accounts/login/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'account/login.html')


class LogoutPageTests(ViewsMixin, TestCase):
    base_url = '/accounts/logout/'

    def test_logout_url_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get('/accounts/logout/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'account/logout.html')


class QuestionsListViewTests(ViewsMixin, TestCase):
    base_url = '/lists/'

    def test_question_list_url_resolves_to_view(self):
        self.create_and_login_a_user()

        found = resolve('/lists/')
        self.assertEqual(
            found.func.__name__, QuestionsListView.as_view().__name__
        )

    def test_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get('/lists/')

        self.assertTemplateUsed(response, 'question_list.html')


class QuestionsListDetailViewTests(ViewsMixin, TestCase):
    base_url = '/lists/an-awesome-list/'

    def setUp(self):
        self.question_list = QuestionListFactory(title='an awesome list')
        question = QuestionFactory(title='cool?', child_of=self.question_list)
        AlternativeFactory(title='yes', question=question)
        AlternativeFactory(title='no', question=question)

    def test_resolves_to_view(self):
        self.create_and_login_a_user()

        found = resolve('/lists/an-awesome-list/')

        self.assertEqual(
            found.func.__name__, AnswerQuestionListView.as_view().__name__
        )

    def test_returns_correct_html(self):
        self.create_and_login_a_user()
        QuestionFactory(title='some question', child_of=self.question_list)

        response = self.client.get('/lists/an-awesome-list/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'question_list_details.html')

    def test_pagination_works(self):
        self.create_and_login_a_user()
        QuestionFactory(title='some question', child_of=self.question_list)
        QuestionFactory(title='another question', child_of=self.question_list)

        response = self.client.get('/lists/an-awesome-list/?page=1')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'question_list_details.html')

        response = self.client.get('/lists/an-awesome-list/?page=1')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'question_list_details.html')

    def test_message_that_you_already_answered_the_question(self):
        self.create_and_login_a_user()
        question_list = QuestionListFactory(title='cool list', owner=self.user)
        question = QuestionFactory(
            title='This is a title for a question',
            child_of=question_list
        )
        AlternativeFactory(title='a1', question=question).users.add(self.user)
        AlternativeFactory(title='a2', question=question).users.add(self.user)

        response = self.client.get('/lists/cool-list/?page=1')
        html = response.content.decode('utf8')

        self.assertRegex(
            html,
            "Question already answered. Your vote won't count this time."
        )

    def test_no_message_that_you_already_answered_the_question(self):
        self.create_and_login_a_user()
        question = QuestionFactory(
            title='some question', child_of=self.question_list
        )
        AlternativeFactory(question=question)

        response = self.client.get('/lists/an-awesome-list/?page=1')
        html = response.content.decode('utf8')

        self.assertNotRegex(
            html,
            "Question already answered. Your vote won't count this time."
        )

    def test_attempt_to_access_an_incomplete_list(self):
        self.create_and_login_a_user()
        QuestionListFactory(title='cool list')

        response = self.client.get('/lists/cool-list/?page=1')
        request = response.wsgi_request
        storage = get_messages(request)
        message = [message.message for message in storage][0]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(message, ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE)


class QuestionsListDetailViewResultsTests(ViewsMixin, TestCase):
    base_url = '/lists/an-awesome-list/results/'

    def setUp(self):
        self.question_list = QuestionListFactory(title='an awesome list')

    def test_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get('/lists/an-awesome-list/results/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'question_list_details_results.html')

    def test_resolves_to_view(self):
        self.create_and_login_a_user()

        found = resolve('/lists/an-awesome-list/results/')

        self.assertEqual(
            found.func.__name__,
            QuestionListResultsView.as_view().__name__
        )

    def test_page_contains_html(self):
        self.create_and_login_a_user()

        response = self.client.get(self.base_url)
        html = response.content.decode('utf8')

        self.assertRegex(
            html, f'These are the results for {self.question_list}!'
        )


class CreateQuestionListViewTests(ViewsMixin, TestCase):
    base_url = '/lists/create/'

    def test_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get('/lists/create/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'create_question_list.html')

    def test_resolves_to_view(self):
        self.create_and_login_a_user()

        found = resolve('/lists/create/')

        self.assertEqual(
            found.func.__name__,
            create_question_list.__name__
        )

    def test_page_contains_title_within_html(self):
        self.create_and_login_a_user()

        response = self.client.get(self.base_url)

        self.assertContains(response, 'Create a question')

    def test_page_contains_form_within_html(self):
        self.create_and_login_a_user()

        response = self.client.get(self.base_url)
        html = response.content.decode('utf8')

        self.assertRegex(html, '<form.*>')
        self.assertRegex(html, '</form>')

    def test_post_success(self):
        self.create_and_login_a_user()

        response = self.client.post(
            self.base_url, data={'title': 'super list'}
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'], '/lists/super-list/add_question/'
        )


class EditQuestionListViewTests(ViewsMixin, TestCase):
    base_url = '/lists/{}/edit/'

    def setUp(self):
        question_list = QuestionListFactory(title='awesome list')
        self.base_url = self.base_url.format(question_list.slug)

    def test_returns_correct_html(self):
        self.create_and_login_a_user()
        QuestionListFactory(title="some list", owner=self.user)

        response = self.client.get('/lists/some-list/edit/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'edit_question_list.html')

    def test_cant_access_if_user_is_not_the_owner(self):
        user_1 = UserFactory(username='Jorge', email='jorge@email.com')
        QuestionListFactory(title="access list", owner=user_1)
        self.create_and_login_a_user()

        response = self.client.get('/lists/access-list/edit/')

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class CreateQuestionViewTests(ViewsMixin, TestCase):
    base_url = '/lists/{}/add_question/'

    def setUp(self):
        self.question_list = QuestionListFactory(title='An amazing list')
        self.base_url = self.base_url.format(self.question_list.slug)

    def test_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get(
            f'/lists/{self.question_list.slug}/add_question/'
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'create_question.html')

    def test_post_complete_list_fail(self):
        self.create_and_login_a_user()

        response = self.client.post(self.base_url, data={})
        messages_list = list(response.context['messages'])
        message = messages_list[0].message

        self.assertFalse(self.question_list.active)
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(message, LIST_COMPLETION_ERROR_MESSAGE)

    def test_post_complete_list_success(self):
        self.create_and_login_a_user()
        question_list = QuestionListFactory(title='An amazing list')
        question = QuestionFactory(title='cool?', child_of=question_list)
        AlternativeFactory(title='yes', question=question)
        AlternativeFactory(title='no', question=question)
        url = f'/lists/{question_list.slug}/add_question/'

        self.client.post(
            url,
            data={}
        )
        modified_list = QuestionList.objects.get(slug=question_list.slug)

        self.assertTrue(modified_list.active)

    def test_post_create_question_success(self):
        self.create_and_login_a_user()

        response = self.client.post(
            self.base_url,
            data={
                'title': 'Is this hard to answer?',
                'alternative_1': 'Yes',
                'alternative_2': 'No'
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            '/lists/an-amazing-list/add_question/'
        )
