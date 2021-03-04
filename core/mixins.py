from http import HTTPStatus

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


class TestViewsMixin:
    def create_and_login_a_user(self, email='javi@email.com'):
        username = email.split('@')[0]
        self.user = get_user_model().objects.create_user(
            email=email, username=username, password='password123'
        )
        self.client.login(email='javi@email.com', password='password123')

    def test_user_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)


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
