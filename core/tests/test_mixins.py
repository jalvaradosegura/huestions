from django.test import TestCase

from ..mixins import TestModelStrMixin


class TestModelStrMixinTests(TestCase):
    def test_model_factory_property(self):
        mixin = TestModelStrMixin()

        self.assertEqual(mixin.model_factory, NotImplemented)
