from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from core.constants import LIST_COMPLETION_ERROR_MESSAGE
from core.mixins import LoginUserMixin
from questions.factories import AlternativeFactory, QuestionFactory

from ..factories import QuestionListFactory
from ..forms import CompleteListForm, CreateQuestionListForm, EditListForm
from ..models import QuestionList


class CompleteListFormTests(TestCase):
    def test_complete_list_with_form_fail(self):
        question_list = QuestionListFactory(title='an awesome list')

        form = CompleteListForm(question_list=question_list)
        form.is_valid()

        self.assertEqual(
            form.custom_error_message, LIST_COMPLETION_ERROR_MESSAGE
        )

    def test_complete_list_with_form_success(self):
        question_list = QuestionListFactory(title='an awesome list')
        question = QuestionFactory(title='cool?', child_of=question_list)
        AlternativeFactory(title='yes', question=question)
        AlternativeFactory(title='no', question=question)

        form = CompleteListForm(question_list=question_list)

        self.assertEqual(form.custom_error_message, '')


class CreateQuestionListFormTests(LoginUserMixin, TestCase):
    def test_get_form_success(self):
        self.create_login_and_verify_user()

        response = self.client.get(reverse('create_list'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, '<label for="id_title"')

    def test_create_question_list_with_form(self):
        self.create_login_and_verify_user()
        form = CreateQuestionListForm(
            data={
                'title': 'Super List',
                'description': 'some cool description',
            },
            owner=self.user,
        )
        form.save()

        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.__str__(), 'Super List')
        self.assertEqual(question_list.description, 'some cool description')

    def test_create_two_question_lists(self):
        self.create_login_and_verify_user()
        form = CreateQuestionListForm(
            data={'title': 'Super List 1'}, owner=self.user
        )
        form.save()
        form = CreateQuestionListForm(
            data={'title': 'Super List 2'}, owner=self.user
        )
        form.save()

        self.assertEqual(QuestionList.objects.count(), 2)

    def test_user_gets_added_to_list_after_creating_one(self):
        self.create_login_and_verify_user()
        form = CreateQuestionListForm(
            data={'title': 'Super List 1'}, owner=self.user
        )
        form.save()

        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.owner.username, 'javi')


class EditListFormTests(TestCase):
    def test_create_list_with_form(self):
        form = EditListForm(data={'title': 'Is this working?'})
        form.save()
        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.__str__(), 'Is this working?')
        self.assertEqual(question_list.slug, 'is-this-working')
        self.assertEqual(QuestionList.objects.all().count(), 1)
