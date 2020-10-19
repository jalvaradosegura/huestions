from django.test import TestCase
from django.urls import resolve

from questions.factory import QuestionFactory, AlternativeFactory
from .views import home
from .models import Question


class HomePageTests(TestCase):
    def setUp(self):
        self.question = QuestionFactory()
        self.alternative = AlternativeFactory(question=self.question)

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
        self.assertIn(self.alternative.alternative, html)


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
