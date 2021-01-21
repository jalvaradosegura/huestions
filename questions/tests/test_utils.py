from django.test import TestCase

from questions.factories import (
    AlternativeFactory,
    QuestionFactory,
    UserFactory
)
from questions.models import Question
from questions.utils import (
    get_possible_questions_for_user,
    get_random_question_for_user
)


class UtilsTests(TestCase):
    def setUp(self):
        QuestionFactory(title='Who is stronger?')
        AlternativeFactory(
            title='Iron Man', question__title='Who is stronger?'
        )
        AlternativeFactory(
            title='Dr. Strange', question__title='Who is stronger?'
        )
        self.user = UserFactory()

    def test_get_random_question_for_user(self):
        question = get_random_question_for_user(self.user)

        self.assertIn(
            question.title, ['Who is stronger?', 'Who is better?']
        )

    def test_get_random_question_for_user_but_he_already_answered_all(self):
        self.make_the_test_user_answer_all_the_questions()
        question = get_random_question_for_user(self.user)

        self.assertEqual(question, None)

    def test_get_possible_questions_for_user_amount(self):
        QuestionFactory(title='another question')
        questions_amount = len(get_possible_questions_for_user(self.user))

        self.assertEqual(questions_amount, 2)

    def test_get_possible_questions_for_user(self):
        possible_questions = get_possible_questions_for_user(self.user)
        all_questions = list(Question.objects.all())

        self.assertEqual(possible_questions, all_questions)

    def test_get_possible_questions_for_user_returns_none(self):
        self.make_the_test_user_answer_all_the_questions()
        possible_questions = get_possible_questions_for_user(self.user)

        self.assertEqual(possible_questions, None)

    def make_the_test_user_answer_all_the_questions(self):
        for question in Question.objects.all():
            first_alternative = question.alternatives.all()[0]
            first_alternative.users.add(self.user)
