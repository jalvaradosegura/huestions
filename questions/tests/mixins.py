from http import HTTPStatus

from django.contrib.auth import get_user_model


class TestStrMixin:
    @property
    def model_factory(self):
        return NotImplemented

    def test_model_str(self):
        model_instance = self.model_factory()
        self.assertEqual(model_instance.__str__(), model_instance.title)


class ViewsMixin:
    @property
    def base_url(self):
        return NotImplemented

    def create_and_login_a_user(self, email='javi@email.com'):
        username = email.split('@')[0]
        self.user = get_user_model().objects.create_user(
            email=email, username=username, password='password123'
        )
        self.client.login(email='javi@email.com', password='password123')

    def test_error(self):
        response = self.client.get(self.base_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
