import factory

from core.constants import TEST_FOLDER_TO_STORE_IMAGES


class DemoListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'demo.DemoList'

    title = 'Demo List'


class DemoQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'demo.DemoQuestion'

    title = 'Who is better?'
    child_of = factory.SubFactory(DemoListFactory)


class DemoAlternativeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'demo.DemoAlternative'

    question = factory.SubFactory(DemoQuestionFactory)
    image = factory.django.ImageField(
        filename=TEST_FOLDER_TO_STORE_IMAGES / 'example.jpg', color='blue'
    )
