from django.contrib.auth import get_user_model
from django.test import TestCase

from ..factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
)
from ..models import Question, QuestionList
from .mixins import TestStrMixin
from users.factories import UserFactory


class QuestionModelTests(TestStrMixin, TestCase):
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
            '/lists/some-title/super-question/1/edit/',
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


class AlternativeModelTests(TestStrMixin, TestCase):
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


class QuestionListModelTests(TestStrMixin, TestCase):
    model_factory = QuestionListFactory

    def test_generate_unique_slug_if_needed(self):
        question_list_1 = self.model_factory(title='This is something awesome')
        question_list_2 = self.model_factory(title='This is something awesome')
        question_list_3 = self.model_factory(title='This is something awesome')

        self.assertEqual(question_list_1.slug, 'this-is-something-awesome')
        self.assertEqual(question_list_2.slug, 'this-is-something-awesome-1')
        self.assertEqual(question_list_3.slug, 'this-is-something-awesome-2')

    def test_get_absolute_url(self):
        question_list_1 = self.model_factory(title='This is something awesome')

        self.assertEqual(
            question_list_1.get_absolute_url(),
            '/lists/this-is-something-awesome/',
        )

    def test_set_owner_of_question_list(self):
        user = UserFactory(username='testuser')
        question_list = self.model_factory(title='awesome list', owner=user)

        self.assertEqual(question_list.owner.username, 'testuser')

    def test_activate_a_list(self):
        question_list = self.model_factory(title='awesome list')

        self.assertFalse(question_list.active)

        question_list.activate()

        self.assertTrue(question_list.active)

    def test_activate_a_list_and_check_it_using_the_manager(self):
        question_list = self.model_factory(title='awesome list')
        question_list.activate()
        question_list.save()

        self.assertTrue(QuestionList.activated_lists.last())

    def test_has_at_least_one_full_question_true(self):
        question_list = self.model_factory(title='awesome list')
        question = QuestionFactory(title='cool?', child_of=question_list)
        AlternativeFactory(title='yes', question=question)
        AlternativeFactory(title='no', question=question)

        self.assertTrue(question_list.has_at_least_one_full_question())

    def test_has_at_least_one_full_question_false(self):
        question_list = self.model_factory(title='awesome list')

        self.assertFalse(question_list.has_at_least_one_full_question())
