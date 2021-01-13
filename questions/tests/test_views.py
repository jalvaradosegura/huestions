from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve

from questions.factories import AlternativeFactory, QuestionFactory
from questions.models import Question
from questions.views import details, home


class BaseForViews(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='javi@email.com',
            username='javi',
            password='password123'
        )
        self.client.login(email='javi@email.com', password='password123')


class HomePageTests(BaseForViews):
    def setUp(self):
        super().setUp()
        self.question = QuestionFactory()
        self.alternative_1 = AlternativeFactory(question=self.question)
        self.alternative_2 = AlternativeFactory(question=self.question)

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')

        self.assertEqual(found.func, home)

    def test_root_url_returns_correct_html(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_contains_latest_question(self):
        last_question = Question.objects.last()

        response = self.client.get('/')
        html = response.content.decode('utf8')

        self.assertIn(last_question.question, html)

    def test_home_page_contains_alternatives(self):
        response = self.client.get('/')
        html = response.content.decode('utf8')

        self.assertIn(self.alternative_1.alternative, html)
        self.assertIn(self.alternative_2.alternative, html)

    def test_home_page_contains_form(self):
        response = self.client.get('/')
        html = response.content.decode('utf8')

        self.assertRegex(html, '<form.*>')
        self.assertRegex(html, '</form>')

    def test_home_page_contains_button_to_vote(self):
        response = self.client.get('/')
        html = response.content.decode('utf8')

        self.assertRegex(html, '<button.* id="button_to_vote">Vote.*</button>')

    def test_home_page_contains_radio_buttons_for_the_alternatives(self):
        response = self.client.get('/')
        html = response.content.decode('utf8')

        self.assertRegex(html, '<input.*type="radio".*id="alternative_1".*>')
        self.assertRegex(html, '<input.*type="radio".*id="alternative_2".*>')

    def test_home_page_redirect_after_post_request(self):
        question = Question.objects.last()
        alternative = self.alternative_1.id

        response = self.client.post(
                '',
                data={'question_id': question.id, 'alternative': alternative}
        )

        self.assertRedirects(response, f'/{question.id}/')


class RandomPageTests(BaseForViews):
    def setUp(self):
        super().setUp()

    def test_root_url_returns_correct_html(self):
        response = self.client.get('/random/')

        self.assertTemplateUsed(response, 'home.html')


class DetailsPageTests(BaseForViews):
    def setUp(self):
        super().setUp()
        self.question = QuestionFactory()
        self.alternative_1 = AlternativeFactory(question=self.question)
        self.alternative_2 = AlternativeFactory(question=self.question)
        self.alternative_1.users.add(self.user)

    def test_details_url_resolves_to_details_page_view(self):
        found = resolve('/1/')

        self.assertEqual(found.func, details)

    def test_details_url_returns_correct_html(self):
        response = self.client.get('/1/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'details.html')

    def test_details_page_contains_question_title(self):
        response = self.client.get('/1/')
        html = response.content.decode('utf8')

        self.assertIn(self.question.question, html)


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


class LogoutPageTests(BaseForViews):
    def setUp(self):
        super().setUp()

    def test_logout_url_returns_correct_html(self):
        response = self.client.get('/accounts/logout/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'account/logout.html')
