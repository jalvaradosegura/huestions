from django.test import TestCase
from django.contrib.auth import get_user_model

from questions.factory import QuestionFactory, AlternativeFactory, UserFactory
from questions.models import Question, Alternative


class QuestionFactoryTests(TestCase):
    def setUp(self):
        QuestionFactory()
        AlternativeFactory.create_batch(2)
        question = QuestionFactory(question='Who is stronger?')
        AlternativeFactory(alternative='Iron Man', question=question)
        AlternativeFactory(alternative='Dr. Strange', question=question)

    def test_question_got_created(self):
        first_question = Question.objects.first()
        last_question = Question.objects.last()
        self.assertEqual(first_question.question, 'Who is better?')
        self.assertEqual(last_question.question, 'Who is stronger?')

    def test_amount_of_questions(self):
        amount_of_questions = Question.objects.all().count()
        self.assertEqual(amount_of_questions, 2)


class AlternativeFactoryTests(TestCase):
    def setUp(self):
        AlternativeFactory()

    def test_alternative_got_created(self):
        alternative = Alternative.objects.last()
        self.assertEqual(alternative.alternative, 'Roger Federer')

    def test_amount_of_alternatives(self):
        amount_of_alternatives = Alternative.objects.all().count()
        self.assertEqual(amount_of_alternatives, 1)

    def test_create_another_alternative(self):
        AlternativeFactory()
        alternative = Alternative.objects.last()
        self.assertEqual(alternative.alternative, 'Rafael Nadal')


class UserFactoryTests(TestCase):
    def setUp(self):
        UserFactory()

    def test_user_got_created(self):
        user = get_user_model().objects.last()
        self.assertEqual(user.username, 'testuser')
