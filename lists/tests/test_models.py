from django.test import TestCase
from django.urls import reverse

from core.mixins import DeleteTestImagesOfAlternativesMixin, TestModelStrMixin
from questions.factories import AlternativeFactory, QuestionFactory
from users.factories import UserFactory

from ..factories import QuestionListFactory
from ..models import QuestionList


class QuestionListModelTests(
    DeleteTestImagesOfAlternativesMixin, TestModelStrMixin, TestCase
):
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
            reverse('answer_list', args=[question_list_1.slug]),
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

    def test_get_unanswered_questions(self):
        user = UserFactory(username='testuser')
        question_list = self.model_factory(title='awesome list', owner=user)
        for _ in range(2):
            question = QuestionFactory(title='cool?', child_of=question_list)
            AlternativeFactory(title='yes', question=question)
            AlternativeFactory(title='no', question=question)
        question = QuestionFactory(title='cool?', child_of=question_list)
        AlternativeFactory(title='yes', question=question)
        alternative = AlternativeFactory(title='no', question=question)

        alternative.vote_for_this_alternative(user)

        self.assertEqual(len(question_list.get_unanswered_questions(user)), 2)

    def test_get_amount_of_unanswered_questions(self):
        user = UserFactory(username='testuser')
        question_list = self.model_factory(title='awesome list', owner=user)
        for _ in range(2):
            question = QuestionFactory(title='cool?', child_of=question_list)
            AlternativeFactory(title='yes', question=question)
            AlternativeFactory(title='no', question=question)
        question = QuestionFactory(title='cool?', child_of=question_list)
        AlternativeFactory(title='yes', question=question)
        alternative = AlternativeFactory(title='no', question=question)

        alternative.vote_for_this_alternative(user)

        self.assertEqual(
            question_list.get_amount_of_unanswered_questions(user), 2
        )
