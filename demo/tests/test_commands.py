import io
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.constants import COMMAND_CREATE_DEMO_SUCCESS_MESSAGE

from ..models import DemoList


class CreateDemoListsCommand(TestCase):
    def test_command_success(self):
        out = io.StringIO()
        call_command('create_demo_list', stdout=out)

        demo_list = DemoList.objects.get(title='Demo List')
        demo_q1 = demo_list.questions.all()[0]
        demo_q2 = demo_list.questions.all()[1]
        demo_q3 = demo_list.questions.all()[2]

        self.assertEqual(demo_list.questions.count(), 3)
        self.assertEqual(demo_q1.alternatives.count(), 2)
        self.assertEqual(demo_q2.alternatives.count(), 2)
        self.assertEqual(demo_q3.alternatives.count(), 2)
        self.assertIn(COMMAND_CREATE_DEMO_SUCCESS_MESSAGE, out.getvalue())

    @patch('demo.management.commands.create_demo_list.IMAGE_1_NAME', 'wrong')
    def test_command_fail(self):
        with self.assertRaises(CommandError):
            call_command('create_demo_list')
