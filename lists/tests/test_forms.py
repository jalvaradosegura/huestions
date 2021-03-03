from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..factories import QuestionListFactory
from ..forms import CompleteListForm, CreateQuestionListForm, EditListForm
from ..models import QuestionList
from questions.constants import LIST_COMPLETION_ERROR_MESSAGE
from questions.factories import AlternativeFactory, QuestionFactory


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


class CreateQuestionListFormTests(TestCase):
    def test_get_form_success(self):
        self.sign_up()

        response = self.client.get('/lists/create/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, '<label for="id_title">Title:')

    def test_create_question_list_with_form(self):
        self.sign_up()
        form = CreateQuestionListForm(
            data={'title': 'Super List'}, owner=self.user
        )
        form.save()

        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.__str__(), 'Super List')

    def test_create_two_question_lists(self):
        self.sign_up()
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
        self.sign_up()
        form = CreateQuestionListForm(
            data={'title': 'Super List 1'}, owner=self.user
        )
        form.save()

        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.owner.username, 'javi')

    def sign_up(self):
        self.user = get_user_model().objects.create_user(
            email='javi@email.com', username='javi', password='password123'
        )
        self.client.login(email='javi@email.com', password='password123')


class EditListFormTests(TestCase):
    def test_create_list_with_form(self):
        form = EditListForm(data={'title': 'Is this working?'})
        form.save()
        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.__str__(), 'Is this working?')
        self.assertEqual(question_list.slug, 'is-this-working')
        self.assertEqual(QuestionList.objects.all().count(), 1)
