from django.test import TestCase
from django.urls import resolve

from .views import home
from .models import Question


class HomePageTests(TestCase):
    def setUp(self):
        self.question = Question.objects.create(
                question='Who is better?'
        )

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_root_url_returns_correct_html(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_contains_last_question(self):
        last_question = Question.objects.last()
        response = self.client.get('/')
        html = response.content.decode('utf8')
        self.assertIn(last_question.question, html)


class QuestionModelTest(TestCase):
    def setUp(self):
        self.question = Question.objects.create(
                question='Who is better?'
        )

    def test_model_str(self):
        self.assertEqual(self.question.__str__(), self.question.question)
