import io

from django.core.management import call_command
from django.test import TestCase
from django.urls import resolve, reverse

from ..models import DemoList
from ..views import AnswerDemoView1, AnswerDemoView2, AnswerDemoView3


class AnswerDemo1ViewTests(TestCase):
    def setUp(self):
        out = io.StringIO()
        call_command('create_demo_list', stdout=out)
        demo_list = DemoList.objects.get(title='Demo List')
        self.base_url = reverse('answer_demo_1', args=[demo_list.id])

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AnswerDemoView1.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, AnswerDemoView1.template_name)


class AnswerDemo2ViewTests(TestCase):
    def setUp(self):
        out = io.StringIO()
        call_command('create_demo_list', stdout=out)
        demo_list = DemoList.objects.get(title='Demo List')
        self.base_url = reverse('answer_demo_2', args=[demo_list.id])

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AnswerDemoView2.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, AnswerDemoView2.template_name)


class AnswerDemo3ViewTests(TestCase):
    def setUp(self):
        out = io.StringIO()
        call_command('create_demo_list', stdout=out)
        demo_list = DemoList.objects.get(title='Demo List')
        self.base_url = reverse('answer_demo_3', args=[demo_list.id])

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AnswerDemoView3.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, AnswerDemoView3.template_name)
