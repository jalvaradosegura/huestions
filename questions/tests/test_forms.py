from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
)
from ..forms import AnswerQuestionForm


class AnswerQuestionFormTests(TestCase):
    def test_generate_the_form_with_choices(self):
        question = QuestionFactory(title='What is this question')
        only_alternative = AlternativeFactory(
            title='Only alternative', question=question
        )

        form = AnswerQuestionForm(question.id)

        for alternative in form.fields['alternatives'].choices:
            self.assertEqual(only_alternative.__str__(), alternative[1])


class AnswerQuestionFormViewTests(TestCase):
    def test_get_success(self):
        question_list = QuestionListFactory(title='awesome list')
        question = QuestionFactory(
            title='awesome question', child_of=question_list
        )
        AlternativeFactory(title='awesome alternative', question=question)
        self.sign_up()

        response = self.client.get('/lists/awesome-list/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, '<label for="id_alternatives_0">Alternatives:', html=True
        )

    def test_post_success_and_adds_user_to_alternative(self):
        question_list = QuestionListFactory(title='awesome list')
        question = QuestionFactory(
            title='awesome question', child_of=question_list
        )
        another_question = QuestionFactory(
            title='another awesome question', child_of=question_list
        )
        AlternativeFactory(title='awesome alternative', question=question)
        AlternativeFactory(
            title='another alternative', question=another_question
        )
        self.sign_up()

        response = self.client.post(
            '/lists/awesome-list/',
            data={
                'alternatives': [1],
                'question_list_id': '1',
                'next_page': '2',
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response['Location'], '/lists/awesome-list/?page=2')
        self.assertEqual(self.user.alternatives_chosen.count(), 1)

    def test_post_and_go_to_results(self):
        question_list = QuestionListFactory(title='awesome list')
        question = QuestionFactory(
            title='awesome question', child_of=question_list
        )
        AlternativeFactory(title='awesome alternative', question=question)
        self.sign_up()

        response = self.client.post(
            '/lists/awesome-list/',
            data={
                'alternatives': [1],
                'question_list_id': '1'
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response['Location'], '/lists/awesome-list/results/')
        self.assertEqual(self.user.alternatives_chosen.count(), 1)

    def sign_up(self):
        self.user = get_user_model().objects.create_user(
            email='javi@email.com', username='javi', password='password123'
        )
        self.client.login(email='javi@email.com', password='password123')
