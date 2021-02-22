from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..constants import LIST_COMPLETION_ERROR_MESSAGE
from ..factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
)
from ..forms import (
    AddAlternativesForm,
    AnswerQuestionForm,
    CompleteListForm,
    CreateQuestionForm,
    CreateQuestionListForm,
)
from ..models import Alternative, Question, QuestionList


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
        AlternativeFactory(title='awesome alternative 1', question=question)
        AlternativeFactory(title='awesome alternative 2', question=question)
        self.sign_up()

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
            },
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
            data={'alternatives': [1], 'question_list_id': '1'},
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response['Location'], '/lists/awesome-list/results/')
        self.assertEqual(self.user.alternatives_chosen.count(), 1)

    def sign_up(self):
        self.user = get_user_model().objects.create_user(
            email='javi@email.com', username='javi', password='password123'
        )
        self.client.login(email='javi@email.com', password='password123')


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


class EditListFormTests(TestCase):
    def test_get_form_success(self):
        self.sign_up()
        question_list = QuestionListFactory(
            title='an awesome list', owner=self.user
        )

        response = self.client.get(f'/lists/{question_list.slug}/edit/')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, '<input type="text" name="list_title"')

    def test_submit_form_success(self):
        self.sign_up()
        question_list = QuestionListFactory(
            title='an awesome list', owner=self.user
        )
        list_id = question_list.id

        self.client.post(
            f'/lists/{question_list.slug}/edit/',
            data={
                'list_title': 'new title',
            },
        )
        question_list = QuestionList.objects.get(id=list_id)

        self.assertEqual(question_list.title, 'new title')

    def sign_up(self):
        self.user = get_user_model().objects.create_user(
            email='javi@email.com', username='javi', password='password123'
        )
        self.client.login(email='javi@email.com', password='password123')


class CreateQuestionFormTests(TestCase):
    def test_get_form_success(self):
        self.sign_up()
        question_list = QuestionListFactory(title='an awesome list')

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

    def sign_up(self):
        self.user = get_user_model().objects.create_user(
            email='javi@email.com', username='javi', password='password123'
        )
        self.client.login(email='javi@email.com', password='password123')


class AddAlternativesFormTests(TestCase):
    def setUp(self):
        self.question_list = QuestionListFactory(title='an awesome list')
        self.question = QuestionFactory(
            title='Is this hard?', child_of=self.question_list
        )

    def test_get_form_success(self):
        self.sign_up()

        response = self.client.get(
            f'/lists/{self.question_list.slug}/add_question/'
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(
            response, '<label for="id_alternative_1">Alternative 1:'
        )
        self.assertContains(
            response, '<label for="id_alternative_2">Alternative 2:'
        )

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
        self.sign_up()
        form = AddAlternativesForm(
            data={'alternative_1': 'yes', 'alternative_2': 'no'},
        )

        if form.is_valid():
            form.save(question=self.question)
        firt_alternative = Alternative.objects.first()
        last_alternative = Alternative.objects.last()

        self.assertEqual(firt_alternative.__str__(), 'Yes')
        self.assertEqual(last_alternative.__str__(), 'No')

    def sign_up(self):
        self.user = get_user_model().objects.create_user(
            email='javi@email.com', username='javi', password='password123'
        )
        self.client.login(email='javi@email.com', password='password123')
