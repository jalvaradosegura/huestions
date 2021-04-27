import io
from http import HTTPStatus

from django.core.management import call_command
from django.test import TestCase
from django.urls import resolve, reverse

from ..models import DemoList
from ..views import (
    AnswerDemoView1,
    AnswerDemoView2,
    AnswerDemoView3,
    DemoResults,
)


class AnswerDemo1ViewTests(TestCase):
    def setUp(self):
        out = io.StringIO()
        call_command('create_demo_list', stdout=out)
        self.demo_list = DemoList.objects.get(title='Demo List')
        self.base_url = reverse('answer_demo_1', args=[self.demo_list.id])

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AnswerDemoView1.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, AnswerDemoView1.template_name)

    def test_post_fail(self):
        response = self.client.post(
            self.base_url,
            data={
                'wrong_key': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            self.demo_list.questions.all()[0].alternatives.all()[0].votes, 0
        )

    def test_post_success_alt_1_option_1(self):
        response = self.client.post(
            self.base_url,
            data={
                'vote_1': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_demo_2', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[0].alternatives.all()[0].votes, 1
        )

    def test_post_success_alt_1_option_2(self):
        response = self.client.post(
            self.base_url,
            data={
                'alternative_1': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_demo_2', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[0].alternatives.all()[0].votes, 1
        )

    def test_post_success_alt_2_option_1(self):
        response = self.client.post(
            self.base_url,
            data={
                'vote_2': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_demo_2', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[0].alternatives.all()[1].votes, 1
        )

    def test_post_success_alt_2_option_2(self):
        response = self.client.post(
            self.base_url,
            data={
                'alternative_2': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_demo_2', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[0].alternatives.all()[1].votes, 1
        )


class AnswerDemo2ViewTests(TestCase):
    def setUp(self):
        out = io.StringIO()
        call_command('create_demo_list', stdout=out)
        self.demo_list = DemoList.objects.get(title='Demo List')
        self.base_url = reverse('answer_demo_2', args=[self.demo_list.id])

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AnswerDemoView2.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, AnswerDemoView2.template_name)

    def test_post_fail(self):
        response = self.client.post(
            self.base_url,
            data={
                'wrong_key': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            self.demo_list.questions.all()[1].alternatives.all()[0].votes, 0
        )

    def test_post_success_alt_1_option_1(self):
        response = self.client.post(
            self.base_url,
            data={
                'vote_1': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_demo_3', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[1].alternatives.all()[0].votes, 1
        )

    def test_post_success_alt_1_option_2(self):
        response = self.client.post(
            self.base_url,
            data={
                'alternative_1': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_demo_3', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[1].alternatives.all()[0].votes, 1
        )

    def test_post_success_alt_2_option_1(self):
        response = self.client.post(
            self.base_url,
            data={
                'vote_2': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_demo_3', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[1].alternatives.all()[1].votes, 1
        )

    def test_post_success_alt_2_option_2(self):
        response = self.client.post(
            self.base_url,
            data={
                'alternative_2': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_demo_3', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[1].alternatives.all()[1].votes, 1
        )


class AnswerDemo3ViewTests(TestCase):
    def setUp(self):
        out = io.StringIO()
        call_command('create_demo_list', stdout=out)
        self.demo_list = DemoList.objects.get(title='Demo List')
        self.base_url = reverse('answer_demo_3', args=[self.demo_list.id])

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AnswerDemoView3.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, AnswerDemoView3.template_name)

    def test_post_fail(self):
        response = self.client.post(
            self.base_url,
            data={
                'wrong_key': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            self.demo_list.questions.all()[2].alternatives.all()[0].votes, 0
        )

    def test_post_success_alt_1_option_1(self):
        response = self.client.post(
            self.base_url,
            data={
                'vote_1': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('demo_results', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[2].alternatives.all()[0].votes, 1
        )

    def test_post_success_alt_1_option_2(self):
        response = self.client.post(
            self.base_url,
            data={
                'alternative_1': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('demo_results', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[2].alternatives.all()[0].votes, 1
        )

    def test_post_success_alt_2_option_1(self):
        response = self.client.post(
            self.base_url,
            data={
                'vote_2': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('demo_results', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[2].alternatives.all()[1].votes, 1
        )

    def test_post_success_alt_2_option_2(self):
        response = self.client.post(
            self.base_url,
            data={
                'alternative_2': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('demo_results', args=[self.demo_list.id]),
        )
        self.assertEqual(
            self.demo_list.questions.all()[2].alternatives.all()[1].votes, 1
        )


class DemoResultsViewTests(TestCase):
    def setUp(self):
        out = io.StringIO()
        call_command('create_demo_list', stdout=out)
        self.demo_list = DemoList.objects.get(title='Demo List')
        self.base_url = reverse('demo_results', args=[self.demo_list.id])

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(found.func.__name__, DemoResults.as_view().__name__)

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, DemoResults.template_name)
