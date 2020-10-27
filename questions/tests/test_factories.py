from django.test import TestCase
from django.contrib.auth import get_user_model

from questions.factory import QuestionFactory, AlternativeFactory, UserFactory
from questions.models import Question, Alternative


class QuestionFactoryTests(TestCase):
    def setUp(self):
        QuestionFactory()

    def test_question_got_created(self):
        question = Question.objects.last()
        self.assertEqual(question.question, 'Who is better?')

    def test_amount_of_questions(self):
        amount_of_questions = Question.objects.all().count()
        self.assertEqual(amount_of_questions, 1)


class AlternativeFactoryTests(TestCase):
    def setUp(self):
        AlternativeFactory()

    def test_alternative_got_created(self):
        alternative = Alternative.objects.last()
        self.assertEqual(alternative.alternative, 'Roger Federer')

    def test_amount_of_alternatives(self):
        amount_of_alternatives = Alternative.objects.all().count()
        self.assertEqual(amount_of_alternatives, 1)


class UserFactoryTests(TestCase):
    def setUp(self):
        UserFactory()

    def test_user_got_created(self):
        user = get_user_model().objects.last()
        self.assertEqual(user.username, 'testuser')
