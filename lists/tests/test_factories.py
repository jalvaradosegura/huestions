from django.test import TestCase

from ..factories import QuestionListFactory
from questions.factories import QuestionFactory


class QuestionListFactoryTests(TestCase):
    def test_question_list_got_created(self):
        question_list = QuestionListFactory(title='some title')

        self.assertEqual(question_list.title, 'some title')

    def test_question_list_has_questions_attached(self):
        question_list = QuestionListFactory(title='some title')
        QuestionFactory(title='first', child_of=question_list)
        QuestionFactory(title='second', child_of=question_list)

        self.assertEqual(question_list.questions.all().count(), 2)
