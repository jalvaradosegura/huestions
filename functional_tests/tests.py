import datetime
import time

from django.test import LiveServerTestCase
from django.contrib.auth import get_user_model

from selenium import webdriver

from questions.factory import QuestionFactory, AlternativeFactory


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.question = QuestionFactory()
        AlternativeFactory.create_batch(2, question=self.question)
        self.user = get_user_model().objects.create_user(
            email='javi@email.com',
            username='javi',
            password='password123'
        )

    def tearDown(self):
        self.browser.quit()

    def test_can_visit_home_page(self):
        # Javi heard about a fun page, where you have to answer hard questions
        # She visits it
        self.browser.get(self.live_server_url)

        # She notices the page title mention Huestion
        self.assertIn('Huestion', self.browser.title)

        # She is received with the latest question
        question = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(self.question.__str__(), question)

        # She realized that the question was created recently by looking at the
        # publication date
        publication_date = self.browser.find_element_by_id(
            'creation_date'
        ).text
        current_date = datetime.datetime.now().strftime('%d-%m-%Y')
        self.assertIn(current_date, publication_date)

        # The question contains 2 alternatives
        alternative_1 = self.browser.find_element_by_id(
            'label_alternative_1'
        ).text
        self.assertEqual(alternative_1, 'Roger Federer')
        alternative_2 = self.browser.find_element_by_id(
            'label_alternative_2'
        ).text
        self.assertEqual(alternative_2, 'Rafael Nadal')

        # She selects one alternative of the form
        selected_alternative = self.browser.find_element_by_id('alternative_1')
        self.assertEqual(
            '1', selected_alternative.get_attribute('value')
        )
        selected_alternative.click()

        # She votes for it by clicking the vote button
        button_to_vote = self.browser.find_element_by_id('button_to_vote')
        button_to_vote.click()

        # Finally she is redirected to the question details
        self.assertIn('Question details', self.browser.title)

        # Javi can see now the details of the question she answered
        question = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(self.question.__str__(), question)

        # She sees what alternatives people have chosen in terms of percentage
        alternative_1_percentage = self.browser.find_element_by_id(
            'alternative_1_percentage'
        ).text
        self.assertIn('100.0%', alternative_1_percentage)
