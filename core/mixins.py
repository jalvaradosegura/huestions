from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin

from allauth.account.models import EmailAddress

from lists.models import QuestionList


class TestModelStrMixin:
    @property
    def model_factory(self):
        return NotImplemented

    def test_model_str(self):
        model_instance = self.model_factory()
        self.assertEqual(model_instance.__str__(), model_instance.title)


class TestViewsMixin:
    def create_and_login_a_user(self, email='javi@email.com'):
        username = email.split('@')[0]
        self.user = get_user_model().objects.create_user(
            email=email, username=username, password='password123'
        )

        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True
        )

        self.client.login(email=email, password='password123')

    def test_user_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_user_havent_verified_its_account_yet(self):
        email_address = EmailAddress.objects.get(email=self.user.email)
        email_address.verified = False
        email_address.save()

        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(
            response, 'account/verified_email_required.html'
        )


class CustomUserPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        if 'list_slug' in self.kwargs:
            slug = self.kwargs['list_slug']
        else:
            slug = self.kwargs['slug']
        question_list = QuestionList.objects.get(slug=slug)

        if (
            self.request.user == question_list.owner
            and question_list.active is False
        ):
            return True
        return False
