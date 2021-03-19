from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.mixins import TestModelStrMixin
from users.factories import UserFactory

from ..factories import AlternativeFactory, QuestionFactory
from ..models import Question


class QuestionModelTests(TestModelStrMixin, TestCase):
    model_factory = QuestionFactory

    def setUp(self):
        self.question = self.model_factory(title='super question')
        self.alternative_1 = AlternativeFactory(
            title='alternative 1', question=self.question
        )
        self.alternative_2 = AlternativeFactory(
            title='alternative 2', question=self.question
        )
        self.user_1 = UserFactory(username='Javi')
        self.user_2 = UserFactory(username='Jorge')
        self.alternative_1.users.add(self.user_1)
        self.alternative_2.users.add(self.user_2)

    def test_get_absolute_url(self):
        self.assertEqual(
            self.question.get_absolute_url(),
            reverse(
                'edit_question',
                args=[
                    self.question.child_of.slug,
                    self.question.slug,
                    self.question.id,
                ],
            ),
        )

    def test_was_created_recently(self):
        self.assertTrue(self.question.was_created_recently())

    def test_question_contains_two_alternatives(self):
        question = Question.objects.last()

        self.assertEqual(question.alternatives.count(), 2)

    def test_get_amount_of_users_that_have_voted_this_question(self):
        votes = self.question.get_amount_of_users_that_have_voted()

        self.assertEqual(votes, 2)

    def test_get_vote_amount_for_each_alternative(self):
        votes_amount = self.question.get_votes_amount_for_each_alternative()

        self.assertEqual(votes_amount, [1, 1])

    def test_get_vote_percentage_for_each_alternative(self):
        percentages = self.question.get_votes_percentage_for_each_alternative()

        self.assertEqual(percentages, [50, 50])

    def test_has_the_user_already_voted(self):
        response = self.question.has_the_user_already_voted(self.user_1)

        self.assertTrue(response)

    def test_is_completed_true(self):
        self.assertTrue(self.question.is_completed())

    def test_is_completed_false(self):
        question = QuestionFactory(title='cool?')
        self.assertFalse(question.is_completed())

    def test_get_user_voted_alternative(self):
        user = UserFactory(username='user')
        question = QuestionFactory(title='cool?')
        AlternativeFactory(title='a1', question=question)
        alternative = AlternativeFactory(title='a2', question=question)

        alternative.vote_for_this_alternative(user)

        self.assertEqual(
            question.get_user_voted_alternative(user),
            alternative
        )

    def test_get_user_voted_alternative_returns_none(self):
        user = UserFactory(username='user')
        question = QuestionFactory(title='cool?')
        AlternativeFactory(title='a1', question=question)
        AlternativeFactory(title='a2', question=question)

        self.assertEqual(question.get_user_voted_alternative(user), None)


class AlternativeModelTests(TestModelStrMixin, TestCase):
    model_factory = AlternativeFactory

    def setUp(self):
        self.alternative = AlternativeFactory()
        self.user = get_user_model().objects.create_user(
            email='javi@email.com', username='javi', password='password123'
        )
        self.alternative.users.add(self.user)

    def test_get_votes_amount(self):
        self.assertEqual(self.alternative.get_votes_amount(), 1)

    def test_get_votes_percentage(self):
        self.assertEqual(self.alternative.get_votes_percentage(), 100)

    def test_get_votes_percentage_with_no_votes(self):
        self.user.delete()

        self.assertEqual(self.alternative.get_votes_percentage(), 0)

    def test_vote_for_this_alternative(self):
        alternative = AlternativeFactory(title='awesome alternative')

        alternative.vote_for_this_alternative(self.user)

        self.assertIn(
            alternative,
            [
                alternative
                for alternative in self.user.alternatives_chosen.all()
            ],
        )
