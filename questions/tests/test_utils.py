from django.test import TestCase

from questions.utils import (
    get_random_question_for_user,
    get_possible_questions_for_user
)
from questions.factory import QuestionFactory, AlternativeFactory, UserFactory
from questions.models import Question


class UtilsTests(TestCase):
    def setUp(self):
        QuestionFactory()
        AlternativeFactory.create_batch(2)
        question = QuestionFactory(question='Who is stronger?')
        AlternativeFactory(alternative='Iron Man', question=question)
        AlternativeFactory(alternative='Dr. Strange', question=question)
        self.user = UserFactory()

    def test_get_random_question_for_user(self):
        question = get_random_question_for_user(self.user)
        self.assertIn(
            question.question, ['Who is stronger?', 'Who is better?']
        )

    def test_get_possible_questions_for_user_amount(self):
        questions_amount = len(get_possible_questions_for_user(self.user))
        self.assertEqual(questions_amount, 2)

    def test_get_possible_questions_for_user(self):
        possible_questions = get_possible_questions_for_user(self.user)
        all_questions = list(Question.objects.all())
        self.assertEqual(possible_questions, all_questions)

    def test_get_possible_questions_for_user_returns_empty(self):
        for question in Question.objects.all():
            first_alternative = question.alternatives.all()[0]
            first_alternative.users.add(self.user)
        possible_questions = get_possible_questions_for_user(self.user)
        self.assertEqual(possible_questions, [])
