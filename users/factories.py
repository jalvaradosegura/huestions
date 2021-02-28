import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'users.CustomUser'
        django_get_or_create = ('username',)

    username = 'testuser'
    email = 'testuser@email.com'
    password = 'hola1234'
