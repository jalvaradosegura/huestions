from django.test import TestCase

from .mixins import TestStrMixin


class TestTestStrMixin(TestCase):
    def test_model_factory_property(self):
        mixin = TestStrMixin()

        self.assertEqual(mixin.model_factory, NotImplemented)
