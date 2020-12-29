import datetime
import time

from django.test import LiveServerTestCase

from selenium import webdriver

from questions.factory import QuestionFactory, AlternativeFactory


def sign_up(browser, email, password):
    # She enter her email and password for sign up
    email_input = browser.find_element_by_id('id_email')
    email_input.send_keys(email)
    password_input = browser.find_element_by_id('id_password1')
    password_input.send_keys(password)

    # She press the signup button
    time.sleep(2)
    browser.find_element_by_tag_name('button').click()


def vote_for_an_alternative(browser, selected_alternative):
    # She selects one alternative of the form
    selected_alternative = browser.find_element_by_id(selected_alternative)
    selected_alternative.click()

    # She votes for it by clicking the vote button
    button_to_vote = browser.find_element_by_id('button_to_vote')
    button_to_vote.click()


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.question = QuestionFactory()
        self.alternative_1 = AlternativeFactory()
        self.alternative_2 = AlternativeFactory()

    def tearDown(self):
        self.browser.quit()

    def test_can_visit_home_page(self):
        # Javi heard about a fun page, where you have to answer hard questions
        # She visits it
        self.browser.get(self.live_server_url)

        # She is asked to login to continue
        # She does not have an account so she click to create one
        dont_have_an_account = self.browser.find_element_by_id(
            'dont_have_an_account'
        )
        dont_have_an_account.click()

        # She creates her account
        sign_up(self.browser, 'javi@email.com', 'super_password_123')

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
        self.assertEqual(alternative_1, self.alternative_1.alternative)
        alternative_2 = self.browser.find_element_by_id(
            'label_alternative_2'
        ).text
        self.assertEqual(alternative_2, self.alternative_2.alternative)

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
        self.assertEqual(message, 'You have already voted for this question')
        time.sleep(3)

    def test_can_visit_random_page(self):
        # Javi visits a section of the page that shows a random question
        self.browser.get(f'{self.live_server_url}/random/')
        # She is asked to login to continue
        # She does not have an account so she click to create one
        dont_have_an_account = self.browser.find_element_by_id(
            'dont_have_an_account'
        )
        dont_have_an_account.click()
        sign_up(self.browser, 'javi@email.com', 'super_password_123')
        self.browser.get(f'{self.live_server_url}/random/')

        self.assertIn('Random Huestion', self.browser.title)
