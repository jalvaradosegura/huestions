from django.contrib.auth import get_user_model
from django.test import TestCase

from questions.factories import (
    AlternativeFactory,
    QuestionFactory,
    UserFactory
)
from questions.models import Alternative, Question


class QuestionFactoryTests(TestCase):
    def setUp(self):
        QuestionFactory()
        AlternativeFactory.create_batch(2)
        AlternativeFactory(
            alternative='Iron Man', question__question='Who is stronger?'
        )
        AlternativeFactory(
            alternative='Dr. Strange', question__question='Who is stronger?'
        )

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
        AlternativeFactory(alternative='Rafael Nadal')

        alternative = Alternative.objects.last()

        self.assertEqual(alternative.alternative, 'Rafael Nadal')


class UserFactoryTests(TestCase):
    def setUp(self):
        UserFactory()

    def test_user_got_created(self):
        user = get_user_model().objects.last()

        self.assertEqual(user.username, 'testuser')
