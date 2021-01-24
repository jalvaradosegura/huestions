import datetime
import time
from unittest import skip

from django.test import LiveServerTestCase
from selenium import webdriver

from questions.factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory
)
from questions.models import Question


def sign_up(browser, email, password, server_url):
    browser.get(f'{server_url}/accounts/signup/')

    # She enter her email and password for sign up
    email_input = browser.find_element_by_id('id_email')
    email_input.send_keys(email)
    password_input = browser.find_element_by_id('id_password1')
    password_input.send_keys(password)

    # She press the signup button
    time.sleep(3)
    browser.find_element_by_tag_name('button').click()


def vote_for_an_alternative(browser, selected_alternative):
    # She selects one alternative of the form
    selected_alternative = browser.find_element_by_id(selected_alternative)
    selected_alternative.click()

    # She votes for it by clicking the vote button
    button_to_vote = browser.find_element_by_id('button_to_vote')
    button_to_vote.click()


class FunctionalTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.question = QuestionFactory()
        self.alternative_1 = AlternativeFactory()
        self.alternative_2 = AlternativeFactory()
        sign_up(
            self.browser,
            'javi@email.com',
            'super_password_123',
            self.live_server_url,
        )

    def tearDown(self):
        self.browser.quit()


class NewVisitorTest(FunctionalTest):
    def setUp(self):
        super().setUp()

    def test_can_visit_home_page(self):
        # Javi heard about a fun page, where you have to answer hard questions
        # She visits it
        # She notices the page title  Huestion
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
        self.assertEqual(alternative_1, self.alternative_1.title)
        alternative_2 = self.browser.find_element_by_id(
            'label_alternative_2'
        ).text
        self.assertEqual(alternative_2, self.alternative_2.title)

        # She selects one alternative of the form
        vote_for_an_alternative(self.browser, 'alternative_1')

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

        # She tries to vote again
        self.browser.get(self.live_server_url)
        message = self.browser.find_element_by_id('you_already_voted').text
        self.assertEqual(
            message,
            'You have already voted for this question or you have answered all the questions.',
        )

    def test_can_visit_random_page(self):
        # Javi visits a section of the page that shows a random question
        self.browser.get(f'{self.live_server_url}/random/')
        self.assertIn('Random Huestion', self.browser.title)

    def test_get_a_different_question_on_each_refresh(self):
        # The system creates some dummy questions
        QuestionFactory(question='Question 2')
        QuestionFactory(question='Question 3')
        all_questions = [
            question.title for question in Question.objects.all()
        ]

        # Now Javi visits the random section, getting a random question each
        # time
        for refresh_iteration in range(2):
            self.browser.get(f'{self.live_server_url}/random/')
            question = self.browser.find_element_by_tag_name('h1').text
            self.assertIn(question, all_questions)

    def test_can_vote_on_random_page(self):
        # Javi visits the random section
        self.browser.get(f'{self.live_server_url}/random/')

        # She votes for an alternativate
        vote_for_an_alternative(self.browser, 'alternative_1')

        # She is redirected to the question details
        self.assertIn('Question details', self.browser.title)


class QuestionListsTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.question_list = QuestionListFactory(title='some cool title')

    def tearDown(self):
        self.browser.quit()

    # @skip("Currently don't want to test")
    def test_can_visit_a_list_of_question_page(self):
        # Javi visits a page that show a list of list questions
        self.browser.get(f'{self.live_server_url}/lists/')

        # She sees a big title that says something abouth the lists
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(title, 'These are the question lists')

        # She selects the first list
        button_to_select = self.browser.find_element_by_id('button_to_select')
        button_to_select.click()

        # She sees the question title in the new url
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/some-cool-title/'
        )

        # She now sees the list title and a question below it
        list_title = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(list_title, 'some cool title')

        # She now sees the first question of the list
        current_page = self.browser.find_element_by_tag_name('span').text
        self.assertIn('1 of ', current_page)

        # She tries to answer the first question
        vote_for_an_alternative(self.browser, 'alternative_1')
        self.fail("Finish the test!")
