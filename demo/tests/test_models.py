from django.test import TestCase

from ..factories import DemoQuestionFactory
from ..models import DemoList


class DemoListModelTests(TestCase):
    def test_model_str(self):
        demo_list = DemoList.objects.create(title='Demo List')
        self.assertEqual(demo_list.__str__(), demo_list.title)


class DemoQuestionModelTests(TestCase):
    def test_model_str(self):
        demo_question = DemoQuestionFactory(title='question')
        self.assertEqual(demo_question.__str__(), demo_question.title)
