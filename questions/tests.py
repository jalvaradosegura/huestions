from django.test import TestCase
from django.urls import resolve
from django.contrib.auth import get_user_model

from questions.factory import QuestionFactory, AlternativeFactory
from .views import home, details
from .models import Question, Alternative


class HomePageTests(TestCase):
    def setUp(self):
        self.question = QuestionFactory()
        self.alternative_1 = AlternativeFactory(question=self.question)
        self.alternative_2 = AlternativeFactory(question=self.question)

    def test_root_url_resolves_to_home_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func, home)

    def test_root_url_returns_correct_html(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_contains_latest_question(self):
        last_question = Question.objects.last()
        response = self.client.get('/')
        html = response.content.decode('utf8')
        self.assertIn(last_question.question, html)

    def test_home_page_contains_alternatives(self):
        response = self.client.get('/')
        html = response.content.decode('utf8')
        self.assertIn(self.alternative_1.alternative, html)
        self.assertIn(self.alternative_2.alternative, html)

    def test_home_page_contains_form(self):
        response = self.client.get('/')
        html = response.content.decode('utf8')
        self.assertRegex(html, '<form.*>')
        self.assertRegex(html, '</form>')

    def test_home_page_contains_button_to_vote(self):
        response = self.client.get('/')
        html = response.content.decode('utf8')
        self.assertRegex(html, '<button.* id="button_to_vote">Vote.*</button>')

    def test_home_page_contains_radio_buttons_for_the_alternatives(self):
        response = self.client.get('/')
        html = response.content.decode('utf8')
        self.assertRegex(html, '<input.*type="radio".*id="alternative_1".*>')
        self.assertRegex(html, '<input.*type="radio".*id="alternative_2".*>')

    def test_home_page_redirect_after_post_request(self):
        question = Question.objects.last()
        alternative = self.alternative_1.id
        response = self.client.post(
                '',
                data={'question_id': question.id, 'alternative': alternative}
        )
        self.assertRedirects(response, f'/{question.id}/')


class DetailsPageTests(TestCase):
    def setUp(self):
        self.question = QuestionFactory()
        self.alternative_1 = AlternativeFactory(question=self.question)
        self.alternative_2 = AlternativeFactory(question=self.question)
        self.user = get_user_model().objects.create_user(
            email='javi@email.com',
            username='javi',
            password='password123'
        )
        self.alternative_1.users.add(self.user)

    def test_details_url_resolves_to_details_page_view(self):
        found = resolve('/1/')
        self.assertEqual(found.func, details)

    def test_details_url_returns_correct_html(self):
        response = self.client.get('/1/')
        self.assertTemplateUsed(response, 'details.html')

    def test_details_page_contains_question_title(self):
        response = self.client.get('/1/')
        html = response.content.decode('utf8')
        self.assertIn(self.question.question, html)


class QuestionModelTest(TestCase):
    def setUp(self):
        self.question = QuestionFactory()
        AlternativeFactory.create_batch(2)

        self.alternative_rafa = Alternative.objects.filter(
            alternative='Rafael Nadal'
        ).first()
        self.alternative_roger = Alternative.objects.filter(
            alternative='Roger Federer'
        ).first()

        self.javi_user = get_user_model().objects.create_user(
            email='javi@email.com',
            username='javi',
            password='password123'
        )
        self.jorge_user = get_user_model().objects.create_user(
            email='jorge@email.com',
            username='jorge',
            password='password123'
        )

        self.javi_user.alternatives_chosen.add(self.alternative_roger)
        self.jorge_user.alternatives_chosen.add(self.alternative_rafa)

    def test_model_str(self):
        self.assertEqual(self.question.__str__(), self.question.question)

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


class AlternativeModelTest(TestCase):
    def setUp(self):
        self.alternative = AlternativeFactory()
        self.user = get_user_model().objects.create_user(
            email='javi@email.com',
            username='javi',
            password='password123'
        )
        self.alternative.users.add(self.user)

    def test_model_str(self):
        self.assertEqual(
            self.alternative.__str__(), self.alternative.alternative
        )

    def test_get_votes_amount(self):
        self.assertEqual(self.alternative.get_votes_amount(), 1)

    def test_get_votes_percentage(self):
        self.assertEqual(self.alternative.get_votes_percentage(), 100)
