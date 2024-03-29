from http import HTTPStatus

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import UserPassesTestMixin

from lists.models import QuestionList


class TestModelStrMixin:
    @property
    def model_factory(self):
        return NotImplemented

    def test_model_str(self):
        model_instance = self.model_factory()
        self.assertEqual(model_instance.__str__(), model_instance.title)


class LoginUserMixin:
    def create_login_and_verify_user(self, email='javi@email.com'):
        username = email.split('@')[0]
        self.user = get_user_model().objects.create_user(
            email=email, username=username, password='password123'
        )

        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True
        )

        self.client.login(email=email, password='password123')


class TestViewsMixin(LoginUserMixin):
    def test_user_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)


class CustomUserPassesTestMixin(UserPassesTestMixin):
    def test_func(self):
        if 'list_slug' in self.kwargs:
            slug = self.kwargs['list_slug']
        elif 'slug' in self.kwargs:
            slug = self.kwargs['slug']
        else:
            user = self.kwargs['username']
            if user == self.request.user.username:
                return True
            return False

        self.instance = QuestionList.objects.select_related('owner').get(
            slug=slug
        )

        if (
            self.request.user == self.instance.owner
            and self.instance.active is False
        ):
            return True
        return False
