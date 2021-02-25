from http import HTTPStatus

from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import resolve

from ..constants import (
    ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE,
    LIST_COMPLETION_ERROR_MESSAGE,
)
from ..factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
    UserFactory,
)
from ..forms import AddAlternativesForm
from ..models import QuestionList
from ..views import (
    AnswerQuestionListView,
    QuestionListResultsView,
    QuestionsListView,
    create_question_list,
    home,
)
from .mixins import ViewsMixin


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
            title='This is a title for a question', child_of=question_list
        )
        AlternativeFactory(title='a1', question=question).users.add(self.user)
        AlternativeFactory(title='a2', question=question).users.add(self.user)

        response = self.client.get('/lists/cool-list/?page=1')
        html = response.content.decode('utf8')

        self.assertRegex(
            html, "Question already answered. Your vote won't count this time."
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
            html, "Question already answered. Your vote won't count this time."
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
            found.func.__name__, QuestionListResultsView.as_view().__name__
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

        self.assertEqual(found.func.__name__, create_question_list.__name__)

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

    def test_post_success(self):
        self.create_and_login_a_user()
        QuestionListFactory(title="access list", owner=self.user)

        response = self.client.post(
            '/lists/access-list/edit/', data={'title': 'another title'}
        )
        question_list = QuestionList.objects.last()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'], '/users/javi/lists/'
        )
        self.assertEqual(question_list.slug, 'another-title')


class CreateQuestionViewTests(ViewsMixin, TestCase):
    base_url = '/lists/{}/add_question/'

    def setUp(self):
        self.question_list = QuestionListFactory(title='An amazing list')
        self.base_url = self.base_url.format(self.question_list.slug)

    def test_returns_correct_html(self):
        self.create_and_login_a_user()
        question_list = QuestionListFactory(title='cool list', owner=self.user)

        response = self.client.get(
            f'/lists/{question_list.slug}/add_question/'
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'create_question.html')

    def test_post_complete_list_fail(self):
        self.create_and_login_a_user()
        question_list = QuestionListFactory(title='cool list', owner=self.user)

        response = self.client.post(
            '/lists/cool-list/add_question/', data={}
        )
        request = response.wsgi_request
        storage = get_messages(request)
        message = [message.message for message in storage][0]

        self.assertFalse(question_list.active)
        self.assertEqual(message, LIST_COMPLETION_ERROR_MESSAGE)
        # self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_complete_list_success(self):
        self.create_and_login_a_user()
        question_list = QuestionListFactory(
            title='An amazing list', owner=self.user
        )
        question = QuestionFactory(title='cool?', child_of=question_list)
        AlternativeFactory(title='yes', question=question)
        AlternativeFactory(title='no', question=question)
        url = f'/lists/{question_list.slug}/add_question/'

        self.client.post(url, data={})
        modified_list = QuestionList.objects.get(slug=question_list.slug)

        self.assertFalse(question_list.active)
        self.assertTrue(modified_list.active)

    def test_post_create_question_success(self):
        self.create_and_login_a_user()
        QuestionListFactory(title='super list', owner=self.user)
        url = '/lists/super-list/add_question/'

        response = self.client.post(
            url,
            data={
                'title': 'Is this hard to answer?',
                'alternative_1': 'Yes',
                'alternative_2': 'No',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'], '/lists/super-list/add_question/'
        )

    def test_cant_access_if_user_is_not_the_owner(self):
        user_1 = UserFactory(username='Jorge', email='jorge@email.com')
        QuestionListFactory(title="access list", owner=user_1)
        self.create_and_login_a_user()

        response = self.client.get('/lists/access-list/add_question/')

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class EditQuestionViewTests(ViewsMixin, TestCase):
    base_url = '/lists/{}/{}/{}/edit/'

    def setUp(self):
        self.question_list = QuestionListFactory(title='An amazing list')
        self.question = QuestionFactory(title='Is this cool?')
        self.base_url = self.base_url.format(
            self.question_list.slug,
            self.question.slug,
            self.question.id,
        )

    def test_returns_correct_html(self):
        self.create_and_login_a_user()
        question_list = QuestionListFactory(title='cool list', owner=self.user)
        question = QuestionFactory(
            title='Is this hard', child_of=question_list
        )

        response = self.client.get(
            f'/lists/{question_list.slug}/{question.slug}/{question.id}/edit/'
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'edit_question.html')

    def test_cant_access_if_user_is_not_the_owner(self):
        user_1 = UserFactory(username='Jorge', email='jorge@email.com')
        question_list = QuestionListFactory(title="access list", owner=user_1)
        question = QuestionFactory(title='what?', child_of=question_list)
        self.create_and_login_a_user()

        response = self.client.get(
            f'/lists/{question_list.slug}/{question.slug}/{question.id}/edit/'
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_pass_alternatives_form_to_context(self):
        self.create_and_login_a_user()
        question_list = QuestionListFactory(title='cool list', owner=self.user)
        question = QuestionFactory(
            title='Is this hard', child_of=question_list
        )
        AlternativeFactory(title="Yes it is", question=question)
        AlternativeFactory(title="No it isn't", question=question)

        response = self.client.get(
            f'/lists/{question_list.slug}/{question.slug}/{question.id}/edit/'
        )

        self.assertIsInstance(
            response.context['alternatives_form'], AddAlternativesForm
        )

    def test_forms_are_being_used_within_template(self):
        self.create_and_login_a_user()
        question_list = QuestionListFactory(title='cool list', owner=self.user)
        question = QuestionFactory(
            title='Is this hard', child_of=question_list
        )
        AlternativeFactory(title="Yes it is", question=question)
        AlternativeFactory(title="No it isn't", question=question)

        response = self.client.get(
            f'/lists/{question_list.slug}/{question.slug}/{question.id}/edit/'
        )
        html = response.content.decode('utf8')

        self.assertRegex(html, '<label for="id_title">')
        self.assertRegex(html, '<label for="id_alternative_1">')
        self.assertRegex(html, '<label for="id_alternative_2">')
