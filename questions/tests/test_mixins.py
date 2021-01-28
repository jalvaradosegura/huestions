from django.test import TestCase

from .mixins import TestStrMixin, ViewsMixin


class TestTestStrMixin(TestCase):
    def test_model_factory_property(self):
        mixin = TestStrMixin()

        self.assertEqual(mixin.model_factory, NotImplemented)


class TestViewsMixin(TestCase):
    def test_base_url_property(self):
        mixin = ViewsMixin()

        self.assertEqual(mixin.base_url, NotImplemented)
