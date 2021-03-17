from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase

from core.constants import LIST_REACHED_MAXIMUM_OF_QUESTION
from core.mixins import LoginUserMixin
from ..factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
)
from ..forms import AddAlternativesForm, AnswerQuestionForm, CreateQuestionForm
from ..models import Alternative, Question


class AnswerQuestionFormTests(TestCase):
    def test_generate_the_form_with_choices(self):
        question = QuestionFactory(title='What is this question')
        only_alternative = AlternativeFactory(
            title='Only alternative', question=question
        )

        form = AnswerQuestionForm(question.id)

        for alternative in form.fields['alternatives'].choices:
            self.assertEqual(only_alternative.__str__(), alternative[1])


class AnswerQuestionFormViewTests(LoginUserMixin, TestCase):
    def test_get_success(self):
        question_list = QuestionListFactory(title='awesome list', active=True)
        question = QuestionFactory(
            title='awesome question', child_of=question_list
        )
        AlternativeFactory(title='awesome alternative 1', question=question)
        AlternativeFactory(title='awesome alternative 2', question=question)
        self.create_login_and_verify_user()

        response = self.client.get('/lists/awesome-list/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, '<label for="id_alternatives_0">Alternatives:'
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
        alternative = AlternativeFactory(
            title='another alternative', question=another_question
        )
        self.create_login_and_verify_user()

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug]),
            data={
                'alternatives': [alternative.id],
                'list_slug': question_list.slug,
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response['Location'], '/lists/awesome-list/')
        self.assertEqual(self.user.alternatives_chosen.count(), 1)

    def test_post_and_go_to_results(self):
        question_list = QuestionListFactory(title='awesome list')
        question = QuestionFactory(
            title='awesome question', child_of=question_list
        )
        alternative = AlternativeFactory(
            title='awesome alternative', question=question
        )
        self.create_login_and_verify_user()

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug]),
            data={
                'alternatives': [alternative.id],
                'list_slug': question_list.slug,
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response['Location'], '/lists/awesome-list/results/')
        self.assertEqual(self.user.alternatives_chosen.count(), 1)


class CreateQuestionFormTests(LoginUserMixin, TestCase):
    def test_get_form_success(self):
        self.create_login_and_verify_user()
        question_list = QuestionListFactory(
            title='an awesome list', owner=self.user
        )

        response = self.client.get(
            f'/lists/{question_list.slug}/add_question/'
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, '<input type="text" name="title"')

    def test_create_question_with_form(self):
        question_list = QuestionListFactory(title='an awesome list')

        form = CreateQuestionForm(
            data={'title': 'Is this working?'}, question_list=question_list
        )
        form.save()
        question = Question.objects.last()

        self.assertEqual(question.__str__(), 'Is this working?')
        self.assertEqual(Question.objects.all().count(), 1)

    def test_create_question_without_question_mark(self):
        question_list = QuestionListFactory(title='an awesome list')

        form = CreateQuestionForm(
            data={'title': 'Who is better'}, question_list=question_list
        )
        form.save()
        question = Question.objects.last()

        self.assertEqual(question.__str__(), 'Who is better?')
        self.assertEqual(Question.objects.all().count(), 1)

    def test_list_reached_the_limit_of_questions(self):
        question_list = QuestionListFactory(title='an awesome list')
        QuestionFactory(title='a', child_of=question_list)
        QuestionFactory(title='a', child_of=question_list)
        QuestionFactory(title='a', child_of=question_list)

        form = CreateQuestionForm(
            data={'title': 'Who is better'}, question_list=question_list
        )
        form.questions_amount_limit = 3
        response = form.is_valid()

        self.assertFalse(response)
        self.assertIn(LIST_REACHED_MAXIMUM_OF_QUESTION, form.errors['__all__'])


class AddAlternativesFormTests(LoginUserMixin, TestCase):
    def setUp(self):
        self.question_list = QuestionListFactory(title='an awesome list')
        self.question = QuestionFactory(
            title='Is this hard?', child_of=self.question_list
        )

    def test_get_form_success(self):
        self.create_login_and_verify_user()
        QuestionListFactory(title='cool list', owner=self.user)

        response = self.client.get('/lists/cool-list/add_question/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, '<label for="id_alternative_1"')
        self.assertContains(response, '<label for="id_alternative_2"')

    def test_add_alternatives_with_form(self):
        form = AddAlternativesForm(
            data={
                'alternative_1': 'Yes it is',
                'alternative_2': 'No it is not',
            }
        )

        if form.is_valid():
            form.save(question=self.question)
        firt_alternative = Alternative.objects.first()
        last_alternative = Alternative.objects.last()

        self.assertEqual(firt_alternative.__str__(), 'Yes it is')
        self.assertEqual(last_alternative.__str__(), 'No it is not')
        self.assertEqual(firt_alternative.question.__str__(), 'Is this hard?')
        self.assertEqual(last_alternative.question.__str__(), 'Is this hard?')
        self.assertEqual(Alternative.objects.all().count(), 2)

    def test_alternatives_all_in_lower_case(self):
        self.create_login_and_verify_user()
        form = AddAlternativesForm(
            data={'alternative_1': 'yes', 'alternative_2': 'no'},
        )

        if form.is_valid():
            form.save(question=self.question)
        firt_alternative = Alternative.objects.first()
        last_alternative = Alternative.objects.last()

        self.assertEqual(firt_alternative.__str__(), 'Yes')
        self.assertEqual(last_alternative.__str__(), 'No')
