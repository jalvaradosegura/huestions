from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse

from core.constants import LIST_COMPLETION_ERROR_MESSAGE, SPECIAL_CHARS_ERROR
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
        self.assertContains(response, 'name="title"')

    def test_create_question_list_with_form(self):
        self.create_login_and_verify_user()

        form = CreateQuestionListForm(
            data={'title': 'Super List', 'tags': 'fun, yay'},
            owner=self.user,
        )
        form.save()
        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.__str__(), 'Super List')
        self.assertFalse(question_list.private)

    def test_create_private_question_list_with_form(self):
        self.create_login_and_verify_user()

        form = CreateQuestionListForm(
            data={'title': 'Super List', 'tags': 'fun, yay', 'private': True},
            owner=self.user,
        )
        form.save()
        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.__str__(), 'Super List')
        self.assertTrue(question_list.private)

    def test_create_question_lists_with_form_that_have_question_mark(self):
        self.create_login_and_verify_user()

        form = CreateQuestionListForm(
            data={'title': 'Listo para la acción?', 'tags': 'fun, yay'},
            owner=self.user,
        )
        form.save()
        question_list_1 = QuestionList.objects.last()
        form = CreateQuestionListForm(
            data={'title': 'Listo para la acción?', 'tags': 'fun, yay'},
            owner=self.user,
        )
        form.save()
        question_list_2 = QuestionList.objects.last()

        self.assertEqual(question_list_1.__str__(), 'Listo para la acción?')
        self.assertEqual(question_list_1.slug, 'listo-para-la-accion')
        self.assertEqual(question_list_2.__str__(), 'Listo para la acción?')
        self.assertEqual(question_list_2.slug, 'listo-para-la-accion-1')

    def test_create_two_question_lists(self):
        self.create_login_and_verify_user()

        form = CreateQuestionListForm(
            data={'title': 'Super List 1', 'tags': 'fun, yay'}, owner=self.user
        )
        form.save()
        form = CreateQuestionListForm(
            data={'title': 'Super List 2', 'tags': 'fun, yay'}, owner=self.user
        )
        form.save()

        self.assertEqual(QuestionList.objects.count(), 2)

    def test_user_gets_added_to_list_after_creating_one(self):
        self.create_login_and_verify_user()
        form = CreateQuestionListForm(
            data={'title': 'Super List 1', 'tags': 'fun, yay'}, owner=self.user
        )
        form.save()

        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.owner.username, 'javi')

    def test_create_list_title_is_too_short_error(self):
        self.create_login_and_verify_user()

        form = CreateQuestionListForm(
            data={
                'title': 'abc',
            },
            owner=self.user,
        )

        self.assertIn(
            'Ensure this value has at least', form.errors['title'][0]
        )

    def test_create_list_with_special_chars_on_title_1(self):
        self.create_login_and_verify_user()

        form = CreateQuestionListForm(
            data={
                'title': '%%%%%%',
            },
            owner=self.user,
        )

        self.assertIn(SPECIAL_CHARS_ERROR, form.errors['title'])

    def test_create_list_with_special_chars_on_title_2(self):
        self.create_login_and_verify_user()

        form = CreateQuestionListForm(
            data={
                'title': 'emoji 😁',
            },
            owner=self.user,
        )

        self.assertIn(SPECIAL_CHARS_ERROR, form.errors['title'])


class EditListFormTests(TestCase):
    def test_create_list_with_form(self):
        form = EditListForm(
            data={'title': 'Is this working', 'tags': 'cool, yay'}
        )
        form.save()
        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.__str__(), 'Is this working')
        self.assertEqual(question_list.slug, 'is-this-working')
        self.assertFalse(question_list.private)
        self.assertEqual(QuestionList.objects.all().count(), 1)

    def test_create_private_list_with_form(self):
        form = EditListForm(
            data={
                'title': 'Is this working',
                'tags': 'cool, yay',
                'private': True,
            }
        )
        form.save()
        question_list = QuestionList.objects.last()

        self.assertEqual(question_list.__str__(), 'Is this working')
        self.assertEqual(question_list.slug, 'is-this-working')
        self.assertTrue(question_list.private)
        self.assertEqual(QuestionList.objects.all().count(), 1)

    def test_edit_list_with_special_chars_on_title(self):
        form = EditListForm(
            data={
                'title': 'emoji 😁',
            },
        )

        self.assertIn(SPECIAL_CHARS_ERROR, form.errors['title'])
