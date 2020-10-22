from django.test import TestCase
from django.urls import resolve

from questions.factory import QuestionFactory, AlternativeFactory
from .views import home, details
from .models import Question


class HomePageTests(TestCase):
    def setUp(self):
        self.question = QuestionFactory()
        self.alternative_1 = AlternativeFactory(question=self.question)
        self.alternative_2 = AlternativeFactory(question=self.question)

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_root_url_returns_correct_html(self):
        response = self.client.get('/')
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
        response = self.client.post(
            '',
            data={'question_id': question.id}
        )
        self.assertRedirects(response, f'/{question.id}/')


class DetailsPageTests(TestCase):
    def setUp(self):
        self.question = QuestionFactory()
        self.alternative_1 = AlternativeFactory(question=self.question)
        self.alternative_2 = AlternativeFactory(question=self.question)

    def test_root_url_resolves_to_details_page_view(self):
        found = resolve('/1/')
        self.assertEqual(found.func, details)

    def test_root_url_returns_correct_html(self):
        response = self.client.get('/1/')
        self.assertTemplateUsed(response, 'details.html')

    def test_details_page_contains_question_title(self):
        response = self.client.get('/1/')
        html = response.content.decode('utf8')
        self.assertIn(self.question.question, html)


class QuestionModelTest(TestCase):
    def setUp(self):
        self.question = QuestionFactory()

    def test_model_str(self):
        self.assertEqual(self.question.__str__(), self.question.question)

    def test_was_created_recently(self):
        self.assertTrue(self.question.was_created_recently())

    def test_question_contains_two_alternatives(self):
        question = Question.objects.last()
        AlternativeFactory.create_batch(2, question=question)
        self.assertEqual(question.alternatives.count(), 2)


class AlternativeModelTest(TestCase):
    def setUp(self):
        self.alternative = AlternativeFactory()

    def test_model_str(self):
        self.assertEqual(
            self.alternative.__str__(),
            self.alternative.alternative
        )
