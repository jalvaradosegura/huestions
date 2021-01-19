from django.contrib.auth import get_user_model
from django.test import TestCase

from questions.factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
)
from questions.models import Alternative, Question


class TestStrMixin:
    @property
    def model_instance(self):
        return NotImplemented

    def test_model_str(self):
        self.assertEqual(
            self.model_instance.__str__(), self.model_instance.title
        )


class QuestionModelTests(TestStrMixin, TestCase):
    model_instance = QuestionFactory()

    def setUp(self):
        AlternativeFactory.create_batch(2)

        self.alternative_rafa = Alternative.objects.filter(
            title='Rafael Nadal'
        ).first()
        self.alternative_roger = Alternative.objects.filter(
            title='Roger Federer'
        ).first()

        self.javi_user = get_user_model().objects.create_user(
            email='javi@email.com', username='javi', password='password123'
        )
        self.jorge_user = get_user_model().objects.create_user(
            email='jorge@email.com', username='jorge', password='password123'
        )

        self.javi_user.alternatives_chosen.add(self.alternative_roger)
        self.jorge_user.alternatives_chosen.add(self.alternative_rafa)

    def test_was_created_recently(self):
        self.assertTrue(self.model_instance.was_created_recently())

    def test_question_contains_two_alternatives(self):
        question = Question.objects.last()

        self.assertEqual(question.alternatives.count(), 2)

    def test_get_amount_of_users_that_have_voted_this_question(self):
        votes = self.model_instance.get_amount_of_users_that_have_voted()

        self.assertEqual(votes, 2)

    def test_get_vote_amount_for_each_alternative(self):
        votes_amount = (
            self.model_instance.get_votes_amount_for_each_alternative()
        )

        self.assertEqual(votes_amount, [1, 1])

    def test_get_vote_percentage_for_each_alternative(self):
        percentages = (
            self.model_instance.get_votes_percentage_for_each_alternative()
        )

        self.assertEqual(percentages, [50, 50])

    def test_has_the_user_already_voted(self):
        response = self.model_instance.has_the_user_already_voted(
            self.javi_user
        )

        self.assertTrue(response)


class AlternativeModelTests(TestStrMixin, TestCase):
    model_instance = AlternativeFactory()

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


class QuestionListModelTests(TestStrMixin, TestCase):
    model_instance = QuestionListFactory()
