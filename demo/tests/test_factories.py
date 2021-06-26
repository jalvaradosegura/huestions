from django.test import TestCase

from core.constants import DEFAULT_IMAGE_NAME
from ..factories import (
    DemoAlternativeFactory,
    DemoListFactory,
    DemoQuestionFactory,
)
from ..models import DemoAlternative, DemoQuestion


class DemoListFactoryTests(TestCase):
    def test_demo_list_got_created(self):
        demo_list = DemoListFactory(title='some title')

        self.assertEqual(demo_list.title, 'some title')


class DemoQuestionFactoryTests(TestCase):
    def test_question_got_created(self):
        first_question = DemoQuestionFactory(title='Who is stronger?')
        last_question = DemoQuestionFactory(title='Who is better?')

        self.assertEqual(first_question.title, 'Who is stronger?')
        self.assertEqual(last_question.title, 'Who is better?')

    def test_amount_of_questions(self):
        DemoQuestionFactory(title='first question')
        DemoQuestionFactory(title='second question')

        amount_of_questions = DemoQuestion.objects.all().count()

        self.assertEqual(amount_of_questions, 2)


class DemoAlternativeFactoryTests(TestCase):
    def setUp(self):
        self.alternative = DemoAlternativeFactory(title='Hello')

    def test_alternative_got_created(self):
        self.assertEqual(self.alternative.title, 'Hello')

    def test_amount_of_alternatives(self):
        amount_of_alternatives = DemoAlternative.objects.all().count()

        self.assertEqual(amount_of_alternatives, 1)

    def test_create_another_alternative(self):
        alternative = DemoAlternativeFactory(title='Rafael Nadal')

        self.assertEqual(alternative.title, 'Rafael Nadal')

    def test_alternative_image(self):
        alternative = DemoAlternativeFactory(title='Hello')
        alternative.image = DEFAULT_IMAGE_NAME
        alternative.save()

        last_alternative = DemoAlternative.objects.last()

        self.assertEqual(
            last_alternative.image.name, DEFAULT_IMAGE_NAME
        )
