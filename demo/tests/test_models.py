from django.test import TestCase

from ..models import DemoList


class DemoListModelTests(TestCase):
    def test_model_str(self):
        demo_list = DemoList.objects.create(title='Demo List')
        self.assertEqual(demo_list.__str__(), demo_list.title)
