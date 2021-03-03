from http import HTTPStatus

from django.contrib.auth import get_user_model


class ViewsMixin:
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
