import io
from http import HTTPStatus

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.management import call_command
from django.test import TestCase
from django.urls import resolve, reverse

from core.constants import (
    ALREADY_ANSWERED_ALL_THE_QUESTIONS,
    ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE,
    DONT_TRY_WEIRD_STUFF,
)
from core.mixins import TestViewsMixin
from demo.factories import DemoListFactory
from lists.models import QuestionList
from users.factories import UserFactory
from votes.models import Vote

from ..factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
)
from ..forms import AddAlternativesForm
from ..models import Alternative, Question
from ..views import (
    AddQuestionView,
    AnswerQuestionView,
    DeleteQuestionView,
    EditQuestionView,
    ImagesCreditView,
    home,
)


class HomePageViewTests(TestCase):
    base_url = reverse('home')

    def setUp(self):
        DemoListFactory()

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve(self.base_url)

        self.assertEqual(found.func, home)

    def test_root_url_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'home.html')


class SignUpPageTests(TestCase):
    def test_signup_url_returns_correct_html(self):
        response = self.client.get(reverse('account_signup'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'account/signup.html')


class LoginPageTests(TestCase):
    def test_login_url_returns_correct_html(self):
        response = self.client.get(reverse('account_login'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'account/login.html')


class LogoutPageTests(TestViewsMixin, TestCase):
    base_url = reverse('account_logout')

    def test_logout_url_returns_correct_html(self):
        self.create_login_and_verify_user()

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'account/logout.html')

    def test_user_havent_verified_its_account_yet(self):
        # This isn't needed for this view
        pass


class AnswerQuestionViewGetTests(TestCase):
    def setUp(self):
        out = io.StringIO()
        call_command('create_demo_list', stdout=out)
        some_list = QuestionListFactory(active=True)
        question_1 = QuestionFactory(child_of=some_list)
        question_2 = QuestionFactory(child_of=some_list)
        AlternativeFactory(question=question_1)
        AlternativeFactory(question=question_2)
        self.base_url = reverse('answer_list', args=[some_list.slug])

    def test_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AnswerQuestionView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(
            response, AnswerQuestionView.template_name_not_auth
        )


class AnswerQuestionViewTests(TestCase):
    def setUp(self):
        self.create_login_and_verify_user()
        self.question_list = QuestionListFactory(
            title='base list', owner=self.user, active=True
        )
        self.base_url = reverse('answer_list', args=[self.question_list.slug])
        question = QuestionFactory(
            title='base question', child_of=self.question_list
        )
        AlternativeFactory(
            title='base alternative 1', question=question
        ).users.add(self.user)
        AlternativeFactory(title='base alternative 2', question=question)
        question = QuestionFactory(
            title='another base question', child_of=self.question_list
        )
        AlternativeFactory(title='base alternative 1', question=question)
        AlternativeFactory(title='base alternative 2', question=question)

    def test_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AnswerQuestionView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, AnswerQuestionView.template_name)

    def test_user_not_logged_in(self):
        call_command('create_demo_list')
        self.client.logout()
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pagination_works(self):
        QuestionFactory(title='some question', child_of=self.question_list)
        QuestionFactory(title='another question', child_of=self.question_list)

        response = self.client.get(self.base_url + '?page=1')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, AnswerQuestionView.template_name)

    def test_user_answered_all_the_questions(self):
        question_list = QuestionListFactory(
            title='no message', active=True, owner=self.user
        )
        question = QuestionFactory(
            title='some question', child_of=question_list
        )
        AlternativeFactory(question=question)
        alternative = AlternativeFactory(question=question)
        alternative.vote_for_this_alternative(self.user)

        response = self.client.get(
            reverse('answer_list', args=[question_list.slug])
        )
        request = response.wsgi_request
        storage = get_messages(request)
        message = [message.message for message in storage][0]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('list_results', args=[question_list.slug]),
        )
        self.assertEqual(message, ALREADY_ANSWERED_ALL_THE_QUESTIONS)

    def test_user_answered_all_the_questions_with_invitation(self):
        user = UserFactory()
        question_list = QuestionListFactory(
            title='no message', active=True, owner=self.user
        )
        question = QuestionFactory(
            title='some question', child_of=question_list
        )
        AlternativeFactory(question=question)
        alternative = AlternativeFactory(question=question)
        alternative.vote_for_this_alternative(self.user)

        response = self.client.get(
            reverse('answer_list', args=[question_list.slug, user])
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('list_results', args=[question_list.slug, user]),
        )

    def test_attempt_to_access_an_unpublished_list(self):
        question_list = QuestionListFactory(title='cool list')

        response = self.client.get(
            reverse('answer_list', kwargs={'slug': question_list.slug})
        )
        request = response.wsgi_request
        storage = get_messages(request)
        message = [message.message for message in storage][0]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(message, ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE)
        self.assertEqual(
            response['Location'],
            reverse('questions_list'),
        )

    def test_post_success(self):
        question_list = QuestionListFactory(title='post list', owner=self.user)
        question = QuestionFactory(
            title='post question', child_of=question_list
        )
        AlternativeFactory(title='post alternative 1', question=question)
        alternative = AlternativeFactory(
            title='post alternative 2', question=question
        )

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug]),
            data={
                'alternatives': alternative.id,
                'list_slug': question_list.slug,
            },
        )
        vote = Vote.objects.last()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('list_results', args=[question_list.slug]),
        )
        self.assertEqual(Vote.objects.last().list.__str__(), 'post list')
        self.assertEqual(vote.shared_by, None)

    def test_post_success_with_invitation_go_to_results(self):
        user = UserFactory()
        question_list = QuestionListFactory(title='post list', owner=self.user)
        question = QuestionFactory(
            title='post question', child_of=question_list
        )
        AlternativeFactory(title='post alternative 1', question=question)
        alternative = AlternativeFactory(
            title='post alternative 2', question=question
        )

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug, user]),
            data={
                'alternatives': alternative.id,
                'list_slug': question_list.slug,
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('list_results', args=[question_list.slug, user]),
        )
        self.assertEqual(Vote.objects.last().list.__str__(), 'post list')

    def test_post_success_with_invitation_go_to_same_view(self):
        user = UserFactory()
        question_list = QuestionListFactory(title='post list', owner=self.user)
        question = QuestionFactory(
            title='post question', child_of=question_list
        )
        AlternativeFactory(title='post alternative 1', question=question)
        alternative = AlternativeFactory(
            title='post alternative 2', question=question
        )
        question = QuestionFactory(
            title='post question', child_of=question_list
        )
        AlternativeFactory(title='post alternative 1', question=question)

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug, user]),
            data={
                'alternatives': alternative.id,
                'list_slug': question_list.slug,
            },
        )
        vote = Vote.objects.last()

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_list', args=[question_list.slug, user]),
        )
        self.assertEqual(Vote.objects.last().list.__str__(), 'post list')
        self.assertEqual(vote.shared_by, user.username)

    def test_post_fail_try_to_vote_for_an_external_alternative(self):
        question_list = QuestionListFactory(title='post list', owner=self.user)
        question = QuestionFactory(
            title='post question', child_of=question_list
        )
        AlternativeFactory(title='post alternative 1', question=question)
        AlternativeFactory(title='post alternative 2', question=question)
        another_list = QuestionListFactory(title='another', owner=self.user)
        another_question = QuestionFactory(
            title='post question', child_of=another_list
        )
        another_alternative = AlternativeFactory(
            title='post alternative 2', question=another_question
        )

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug]),
            data={'alternatives': another_alternative.id},
        )
        request = response.wsgi_request
        storage = get_messages(request)
        message = [message.message for message in storage][0]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_list', args=[question_list.slug]),
        )
        self.assertEqual(message, DONT_TRY_WEIRD_STUFF)

    def test_post_fail_try_to_vote_for_an_external_alternative_list_shared(
        self,
    ):
        question_list = QuestionListFactory(title='post list', owner=self.user)
        question = QuestionFactory(
            title='post question', child_of=question_list
        )
        AlternativeFactory(title='post alternative 1', question=question)
        AlternativeFactory(title='post alternative 2', question=question)
        another_list = QuestionListFactory(title='another', owner=self.user)
        another_question = QuestionFactory(
            title='post question', child_of=another_list
        )
        another_alternative = AlternativeFactory(
            title='post alternative 2', question=another_question
        )
        another_user = UserFactory(username='Jorge', email='jorge@email.com')

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug, another_user]),
            data={'alternatives': another_alternative.id},
        )
        request = response.wsgi_request
        storage = get_messages(request)
        message = [message.message for message in storage][0]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_list', args=[question_list.slug, another_user]),
        )
        self.assertEqual(message, DONT_TRY_WEIRD_STUFF)

    def test_post_fail_try_to_vote_for_a_non_existent_alternative(self):
        question_list = QuestionListFactory(title='post list', owner=self.user)
        question = QuestionFactory(
            title='post question', child_of=question_list
        )
        AlternativeFactory(title='post alternative 1', question=question)
        AlternativeFactory(title='post alternative 2', question=question)
        non_existent_id = Alternative.objects.last().id + 1_000

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug]),
            data={'alternatives': non_existent_id},
        )
        request = response.wsgi_request
        storage = get_messages(request)
        message = [message.message for message in storage][0]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_list', args=[question_list.slug]),
        )
        self.assertEqual(message, DONT_TRY_WEIRD_STUFF)

    def test_post_fail_try_to_vote_for_a_non_existent_alternative_list_shared(
        self,
    ):
        question_list = QuestionListFactory(title='post list', owner=self.user)
        question = QuestionFactory(
            title='post question', child_of=question_list
        )
        AlternativeFactory(title='post alternative 1', question=question)
        AlternativeFactory(title='post alternative 2', question=question)
        non_existent_id = Alternative.objects.last().id + 1_000
        another_user = UserFactory(username='Jorge', email='jorge@email.com')

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug, another_user]),
            data={'alternatives': non_existent_id},
        )
        request = response.wsgi_request
        storage = get_messages(request)
        message = [message.message for message in storage][0]

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_list', args=[question_list.slug, another_user]),
        )
        self.assertEqual(message, DONT_TRY_WEIRD_STUFF)

    def create_login_and_verify_user(self, email='javi@email.com'):
        username = email.split('@')[0]
        self.user = get_user_model().objects.create_user(
            email=email, username=username, password='password123'
        )

        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True
        )

        self.client.login(email=email, password='password123')


class AddQuestionViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_login_and_verify_user()
        self.question_list = QuestionListFactory(
            title='An amazing list', owner=self.user
        )
        self.base_url = reverse('add_question', args=[self.question_list.slug])

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, AddQuestionView.template_name)

    def test_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, AddQuestionView.as_view().__name__
        )

    def test_post_create_question_and_publish_success(self):
        response = self.client.post(
            self.base_url,
            data={
                'title': 'is this hard to answer?',
                'alternative_1': 'yes',
                'alternative_2': 'no',
                'create_and_publish': '',
            },
        )
        request = response.wsgi_request
        question_list = QuestionList.objects.get(id=self.question_list.id)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('lists', args=[request.user]),
        )
        self.assertTrue(question_list.active)

    def test_post_create_question_and_add_another_success(self):
        response = self.client.post(
            self.base_url,
            data={
                'title': 'is this hard to answer?',
                'alternative_1': 'yes',
                'alternative_2': 'no',
                'create_and_add_another': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('add_question', args=[self.question_list.slug]),
        )

    def test_post_create_question_and_go_back(self):
        response = self.client.post(
            self.base_url,
            data={
                'title': 'is this hard to answer?',
                'alternative_1': 'yes',
                'alternative_2': 'no',
                'create_and_go_back': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('edit_list', args=[self.question_list.slug]),
        )

    def test_post_fail(self):
        response = self.client.post(
            self.base_url,
            data={
                'title': '-' * 101,
                'alternative_1': 'yes',
                'alternative_2': 'no',
                'create_and_go_back': '',
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, AddQuestionView.template_name)

    def test_cant_access_if_user_is_not_the_owner(self):
        user_1 = UserFactory(username='Jorge', email='jorge@email.com')
        question_list = QuestionListFactory(title='access list', owner=user_1)

        response = self.client.get(
            reverse('add_question', kwargs={'list_slug': question_list.slug})
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_cant_access_if_list_is_already_published(self):
        question_list = QuestionListFactory(
            title='a list', owner=self.user, active=True
        )

        response = self.client.get(
            reverse('add_question', kwargs={'list_slug': question_list.slug})
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class EditQuestionViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_login_and_verify_user()
        self.question_list = QuestionListFactory(
            title='An amazing list', owner=self.user
        )
        self.question = QuestionFactory(
            title='what?', child_of=self.question_list
        )
        self.alternative_1 = AlternativeFactory(
            title='Yes it is', question=self.question
        )
        self.alternative_2 = AlternativeFactory(
            title="No it isn't", question=self.question
        )
        self.base_url = reverse(
            'edit_question',
            kwargs={
                'list_slug': self.question_list.slug,
                'slug': self.question.slug,
                'question_id': self.question.id,
            },
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, EditQuestionView.template_name)

    def test_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, EditQuestionView.as_view().__name__
        )

    def test_cant_access_if_user_is_not_the_owner(self):
        user_1 = UserFactory(username='Jorge', email='jorge@email.com')
        question_list = QuestionListFactory(title='access list', owner=user_1)
        question = QuestionFactory(title='what?', child_of=question_list)
        AlternativeFactory(title='Yes it is', question=question)
        AlternativeFactory(title="No it isn't", question=question)

        response = self.client.get(
            reverse(
                'edit_question',
                kwargs={
                    'list_slug': question_list.slug,
                    'slug': question.slug,
                    'question_id': question.id,
                },
            )
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_cant_access_if_list_is_already_published(self):
        self.question_list.active = True
        self.question_list.save()

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_pass_alternatives_form_to_context(self):
        response = self.client.get(self.base_url)

        self.assertIsInstance(
            response.context['alternatives_form'], AddAlternativesForm
        )

    def test_forms_are_being_used_within_template(self):
        response = self.client.get(self.base_url)
        html = response.content.decode('utf8')

        self.assertRegex(html, 'id="id_title"')
        self.assertRegex(html, 'id="id_alternative_1"')
        self.assertRegex(html, 'id="id_alternative_2"')

    def test_post_success(self):
        response = self.client.post(
            self.base_url,
            data={
                'title': 'edited??',
                'alternative_1': 'edited',
                'alternative_2': 'edited',
            },
        )
        edited_question = Question.objects.get(id=self.question.id)
        edited_alternative_1 = Alternative.objects.get(
            id=self.alternative_1.id
        )
        edited_alternative_2 = Alternative.objects.get(
            id=self.alternative_2.id
        )

        self.assertEqual(edited_question.title, 'edited??')
        self.assertEqual(edited_alternative_1.title, 'Edited')
        self.assertEqual(edited_alternative_2.title, 'Edited')
        self.assertEqual(
            response['Location'],
            reverse('edit_list', kwargs={'slug': self.question_list.slug}),
        )

    def test_post_fail(self):
        response = self.client.post(
            self.base_url,
            data={
                'title': 'edited',
                'alternative_1': 'edited %',
                'alternative_2': 'edited',
            },
        )

        self.assertTemplateUsed(response, EditQuestionView.template_name)


class DeleteQuestionViewTests(TestViewsMixin, TestCase):
    def setUp(self):
        self.create_login_and_verify_user()
        self.question_list = QuestionListFactory(
            title='test error list', owner=self.user
        )
        question = QuestionFactory(title='cool?', child_of=self.question_list)
        self.base_url = reverse(
            'delete_question',
            kwargs={'slug': self.question_list.slug, 'id': question.id},
        )

    def test_question_list_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, DeleteQuestionView.as_view().__name__
        )

    def test_post_success(self):
        response = self.client.post(self.base_url, data={})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('edit_list', kwargs={'slug': self.question_list.slug}),
        )


class ImagesCreditViewTests(TestCase):
    def setUp(self):
        question_list = QuestionListFactory(active=True)
        self.base_url = reverse('images_credit', args=[question_list.slug])

    def test_url_resolves_to_view(self):
        found = resolve(self.base_url)

        self.assertEqual(
            found.func.__name__, ImagesCreditView.as_view().__name__
        )

    def test_returns_correct_html(self):
        response = self.client.get(self.base_url)

        self.assertTemplateUsed(response, ImagesCreditView.template_name)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_list_not_actived(self):
        question_list = QuestionListFactory()
        url = reverse('images_credit', args=[question_list.slug])

        response = self.client.get(url)

        self.assertTemplateUsed(response, 'errors/404.html')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
