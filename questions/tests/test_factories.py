from django.contrib.auth import get_user_model
from django.test import TestCase

from questions.factories import (
    AlternativeFactory,
    QuestionFactory,
    UserFactory,
    QuestionListFactory
)
from questions.models import Alternative, Question


class QuestionListFactoryTests(TestCase):
    def test_question_list_got_created(self):
        question_list = QuestionListFactory(title='some title')

        self.assertEqual(question_list.title, 'some title')

    def test_question_list_has_questions_attached(self):
        question_list = QuestionListFactory(title='some title')
        QuestionFactory(title='first', child_of=question_list)
        QuestionFactory(title='second', child_of=question_list)

        self.assertEqual(question_list.questions.all().count(), 2)


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


class AlternativeFactoryTests(TestCase):
    def setUp(self):
        AlternativeFactory()

    def test_alternative_got_created(self):
        alternative = Alternative.objects.last()

        self.assertEqual(alternative.title, 'Roger Federer')

    def test_amount_of_alternatives(self):
        amount_of_alternatives = Alternative.objects.all().count()

        self.assertEqual(amount_of_alternatives, 1)

    def test_create_another_alternative(self):
        AlternativeFactory(title='Rafael Nadal')

        alternative = Alternative.objects.last()

        self.assertEqual(alternative.title, 'Rafael Nadal')


class UserFactoryTests(TestCase):
    def setUp(self):
        UserFactory()

    def test_user_got_created(self):
        user = get_user_model().objects.last()

        self.assertEqual(user.username, 'testuser')
