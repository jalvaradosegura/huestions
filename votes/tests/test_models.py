from django.test import TestCase

from ..factories import VoteFactory


class VoteModelTests(TestCase):
    def test_model_str(self):
        vote = VoteFactory()
        self.assertEqual(vote.__str__(), f'{vote.user} vote')
