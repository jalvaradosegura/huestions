from django.test import TestCase

from ..factories import VoteFactory


class VoteFactoryTests(TestCase):
    def test_vote_got_created(self):
        vote = VoteFactory()

        self.assertEqual(vote.list.__str__(), 'some title')
