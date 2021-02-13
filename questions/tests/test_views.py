from http import HTTPStatus

from django.test import TestCase
from django.urls import resolve

from ..factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
)
from .mixins import ViewsMixin
from ..models import Question
from ..views import (
    QuestionsListDetailView,
    QuestionsListListView,
    QuestionsListDetailViewResults,
    details,
    home,
    create_question_list
)


class HomePageTests(ViewsMixin, TestCase):
    base_url = '/'

    def setUp(self):
        self.question = QuestionFactory()
        self.alternative_1 = AlternativeFactory(question=self.question)
        self.alternative_2 = AlternativeFactory(question=self.question)

    def test_root_url_resolves_to_home_page_view(self):
        self.create_and_login_a_user()

        found = resolve('/')

        self.assertEqual(found.func, home)

    def test_root_url_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get('/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_contains_latest_question(self):
        self.create_and_login_a_user()

        last_question = Question.objects.last()

        response = self.client.get('/')
        html = response.content.decode('utf8')

        self.assertIn(last_question.title, html)

    def test_home_page_contains_alternatives(self):
        self.create_and_login_a_user()

        response = self.client.get('/')
        html = response.content.decode('utf8')

        self.assertIn(self.alternative_1.title, html)
        self.assertIn(self.alternative_2.title, html)

    def test_home_page_contains_form(self):
        self.create_and_login_a_user()

        response = self.client.get('/')
        html = response.content.decode('utf8')

        self.assertRegex(html, '<form.*>')
        self.assertRegex(html, '</form>')

    def test_home_page_contains_button_to_vote(self):
        self.create_and_login_a_user()

        response = self.client.get('/')
        html = response.content.decode('utf8')

        self.assertRegex(html, '<button.* id="button_to_vote">Vote.*</button>')

    def test_home_page_contains_radio_buttons_for_the_alternatives(self):
        self.create_and_login_a_user()

        response = self.client.get('/')
        html = response.content.decode('utf8')

        self.assertRegex(html, '<input.*type="radio".*id="alternative_1".*>')
        self.assertRegex(html, '<input.*type="radio".*id="alternative_2".*>')

    def test_home_page_redirect_after_post_request(self):
        self.create_and_login_a_user()

        question = Question.objects.last()
        alternative = self.alternative_1.id

        response = self.client.post(
            '', data={'question_id': question.id, 'alternative': alternative}
        )

        self.assertRedirects(response, f'/{question.id}/')


class RandomPageTests(ViewsMixin, TestCase):
    base_url = '/random/'

    def test_root_url_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get('/random/')

        self.assertTemplateUsed(response, 'home.html')


class DetailsPageTests(ViewsMixin, TestCase):
    base_url = '/1/'

    def setUp(self):
        self.question = QuestionFactory()
        self.alternative_1 = AlternativeFactory(question=self.question)
        self.alternative_2 = AlternativeFactory(question=self.question)

    def test_details_url_resolves_to_details_page_view(self):
        self.create_and_login_a_user()
        self.alternative_1.users.add(self.user)

        found = resolve('/1/')

        self.assertEqual(found.func, details)

    def test_details_url_returns_correct_html(self):
        self.create_and_login_a_user()
        self.alternative_1.users.add(self.user)

        response = self.client.get('/1/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'details.html')

    def test_details_page_contains_question_title(self):
        self.create_and_login_a_user()
        self.alternative_1.users.add(self.user)

        response = self.client.get('/1/')
        html = response.content.decode('utf8')

        self.assertIn(self.question.title, html)


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
            found.func.__name__, QuestionsListListView.as_view().__name__
        )

    def test_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get('/lists/')

        self.assertTemplateUsed(response, 'question_list.html')


class QuestionsListDetailViewTests(ViewsMixin, TestCase):
    base_url = '/lists/an-awesome-list/'

    def setUp(self):
        self.question_list = QuestionListFactory(title='an awesome list')

    def test_resolves_to_view(self):
        self.create_and_login_a_user()

        found = resolve('/lists/an-awesome-list/')

        self.assertEqual(
            found.func.__name__, QuestionsListDetailView.as_view().__name__
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
        question = QuestionFactory(
            title='some question', child_of=self.question_list
        )
        AlternativeFactory(question=question).users.add(self.user)

        response = self.client.get('/lists/an-awesome-list/?page=1')
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
            QuestionsListDetailViewResults.as_view().__name__
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

    def test_post_success(self):
        self.create_and_login_a_user()

        response = self.client.post(
            self.base_url, data={'title': 'Is this hard to answer?'}
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            '/lists/an-amazing-list/is-this-hard-to-answer/1/add_alternatives/'
        )


class AddAlternativesViewTests(ViewsMixin, TestCase):
    base_url = '/lists/{}/{}/{}/add_alternatives/'

    def setUp(self):
        question_list = QuestionListFactory(title='awesome list')
        question = QuestionFactory(
            title='who is the best?', child_of=question_list
        )
        self.base_url = self.base_url.format(
            question_list.slug, question.slug, question.id
        )

    def test_returns_correct_html(self):
        self.create_and_login_a_user()

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'add_alternatives.html')

    def test_post_success(self):
        self.create_and_login_a_user()

        response = self.client.post(
                self.base_url,
                data={'alternative_1': 'Corgis', 'alternative_2': 'Corgis!!'}
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            '/lists/awesome-list/add_question/'
        )
