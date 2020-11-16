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
        # AlternativeFactory.create_batch(2, question=self.question)
        self.alternative_1 = AlternativeFactory()
        self.alternative_2 = AlternativeFactory()
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
        self.assertEqual(alternative_1, self.alternative_1.alternative)
        alternative_2 = self.browser.find_element_by_id(
            'label_alternative_2'
        ).text
        self.assertEqual(alternative_2, self.alternative_2.alternative)

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


class VisitorSignUpLogIn(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_signup_with_email_and_password_only(self):
        # Javi wants to signup on this cool website, so she goes to for it
        self.browser.get(f'{self.live_server_url}/accounts/signup/')

        # She enter her email and password
        email_input = self.browser.find_element_by_id('id_email')
        email_input.send_keys('javi@email.com')
        password_input = self.browser.find_element_by_id('id_password1')
        password_input.send_keys('super_password_123')

        # She press the signup button
        self.browser.find_element_by_tag_name('button').click()
        javi = get_user_model().objects.last()
        self.assertEqual(javi.email, 'javi@email.com')

    def test_signup_logout_login(self):
        # Javi is asked by the website owner to test the workflow:
        # signup -> logout -> login
        self.browser.get(f'{self.live_server_url}/accounts/signup/')

        # She enter her email and password for sign up
        email_input = self.browser.find_element_by_id('id_email')
        email_input.send_keys('javi@email.com')
        password_input = self.browser.find_element_by_id('id_password1')
        password_input.send_keys('super_password_123')

        # She press the signup button
        self.browser.find_element_by_tag_name('button').click()

        # She is signed up
        javi = get_user_model().objects.last()
        self.assertEqual(javi.email, 'javi@email.com')

        # She goes to the logout page
        go_to_logout_button = self.browser.find_element_by_id('logout_button')
        response = go_to_logout_button.click()
        self.assertTemplateUsed(response, 'account/logout.html')

        # She press the logout button
        logout_button = self.browser.find_element_by_tag_name('button')
        logout_button.click()

        # She goes to the login page
        go_to_login_button = self.browser.find_element_by_id('login_button')
        response = go_to_login_button.click()
        self.assertTemplateUsed(response, 'account/login.html')

        # She logs in
        email_input = self.browser.find_element_by_id('id_login')
        email_input.send_keys('javi@email.com')
        password_input = self.browser.find_element_by_id('id_password')
        password_input.send_keys('super_password_123')
        login_button = self.browser.find_element_by_tag_name('button')
        login_button.click()
