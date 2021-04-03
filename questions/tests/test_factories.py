from django.test import TestCase

from core.mixins import DeleteTestImagesOfAlternativesMixin

from ..factories import AlternativeFactory, QuestionFactory
from ..models import Alternative, Question


class QuestionFactoryTests(TestCase):
    def test_question_got_created(self):
        first_question = QuestionFactory(title='Who is stronger?')
        last_question = QuestionFactory(title='Who is better?')

        self.assertEqual(first_question.title, 'Who is stronger?')
        self.assertEqual(last_question.title, 'Who is better?')

    def test_amount_of_questions(self):
        QuestionFactory(title='first question')
        QuestionFactory(title='second question')

        amount_of_questions = Question.objects.all().count()

        self.assertEqual(amount_of_questions, 2)


class AlternativeFactoryTests(DeleteTestImagesOfAlternativesMixin, TestCase):
    def setUp(self):
        self.alternative = AlternativeFactory(title='Hello')

    def test_alternative_got_created(self):
        self.assertEqual(self.alternative.title, 'Hello')

    def test_amount_of_alternatives(self):
        amount_of_alternatives = Alternative.objects.all().count()

        self.assertEqual(amount_of_alternatives, 1)

    def test_create_another_alternative(self):
        alternative = AlternativeFactory(title='Rafael Nadal')

        self.assertEqual(alternative.title, 'Rafael Nadal')
