from django.test import TestCase
from django.urls import resolve, reverse

from ..views import (
    AnswerDemoView1,
    AnswerDemoView2,
    AnswerDemoView3,
    DemoHomeView
)
from ..models import DemoList


class DemoHomeViewTests(TestCase):
    base_url = reverse('demo_home')

    def setUp(self):
        DemoList.objects.create(title='Demo food list')
        DemoList.objects.create(title='Demo sports list')
        DemoList.objects.create(title='Demo movies & tv series list')

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, DemoHomeView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, DemoHomeView.template_name)


class AnswerDemo1ViewTests(TestCase):
    def setUp(self):
        demo_list = DemoList.objects.create(title='Demo list')
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
        demo_list = DemoList.objects.create(title='Demo list')
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
        demo_list = DemoList.objects.create(title='Demo list')
        self.base_url = reverse('answer_demo_3', args=[demo_list.id])

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AnswerDemoView3.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, AnswerDemoView3.template_name)
