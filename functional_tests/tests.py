import datetime
import time

from django.test import LiveServerTestCase
from selenium import webdriver

from questions.constants import LIST_COMPLETION_ERROR_MESSAGE
from questions.factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
)
from questions.models import Question, QuestionList


def vote_for_an_alternative(browser, selected_alternative):
    # She selects one alternative of the form
    selected_alternative = browser.find_element_by_id(selected_alternative)
    selected_alternative.click()

    # She votes for it by clicking the vote button
    button_to_vote = browser.find_element_by_id('button_to_vote')
    button_to_vote.click()


class FunctionalTestsBase(LiveServerTestCase):
    def tearDown(self):
        self.browser.quit()

    def sign_up(self, email, password):
        self.browser.get(f'{self.live_server_url}/accounts/signup/')

        # She enter her email and password for sign up
        email_input = self.browser.find_element_by_id('id_email')
        email_input.send_keys(email)
        password_input = self.browser.find_element_by_id('id_password1')
        password_input.send_keys(password)

        # She press the signup button
        time.sleep(3)
        self.browser.find_element_by_tag_name('button').click()


class NewVisitorTest(FunctionalTestsBase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.sign_up('javi@email.com', 'super_password_123')
        self.question = QuestionFactory(title='some question')
        self.alternative_1 = AlternativeFactory(
            title='alternative 1', question=self.question
        )
        self.alternative_2 = AlternativeFactory(
            title='alternative 2', question=self.question
        )

    def test_can_visit_home_page(self):
        # Javi heard about a fun page, where you have to answer hard questions
        # She visits it
        self.browser.get(f'{self.live_server_url}/')

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
            (
                'You have already voted for this question or you have '
                'answered all the questions.'
            ),
        )

    def test_can_visit_random_page(self):
        # Javi visits a section of the page that shows a random question
        self.browser.get(f'{self.live_server_url}/random/')
        self.assertIn('Random Huestion', self.browser.title)

    def test_get_a_different_question_on_each_refresh(self):
        # The system creates some dummy questions
        QuestionFactory(title='Question 2')
        QuestionFactory(title='Question 3')
        all_questions = [question.title for question in Question.objects.all()]

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


class QuestionListsTest(FunctionalTestsBase):
    def setUp(self):
        self.browser = webdriver.Firefox()

        self.sign_up('javi@email.com', 'super_password_123')

        self.question_list = QuestionListFactory(
            title='some cool title', active=True
        )

        self.question = QuestionFactory(
            title='some question', child_of=self.question_list
        )
        AlternativeFactory(title='some alternative', question=self.question)
        AlternativeFactory(title='some alternative', question=self.question)

        self.another_question = QuestionFactory(
            title='another question', child_of=self.question_list
        )
        AlternativeFactory(
            title='some alternative', question=self.another_question
        )

    def test_can_visit_a_list_of_question_page(self):
        # Javi visits a page that show a list of list questions
        self.browser.get(f'{self.live_server_url}/lists/')

        time.sleep(3)
        # She sees a big title that says something abouth the lists
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(title, 'These are the question lists')

        # She selects the first list
        button_to_select = self.browser.find_element_by_id('button_to_select')
        button_to_select.click()

        # She sees the question title in the new url
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/some-cool-title/',
        )

        # She now sees the list title and a question below it
        list_title = self.browser.find_element_by_tag_name('p').text
        self.assertEqual(list_title, 'some cool title')

        # She now sees the first question of the list
        current_page = self.browser.find_element_by_tag_name('span').text
        self.assertIn('1 of ', current_page)

        # She answer the first question
        vote_for_an_alternative(self.browser, 'id_alternatives_0')
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/some-cool-title/?page=2',
        )

        # She answer the next question
        vote_for_an_alternative(self.browser, 'id_alternatives_0')
        results_title = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('These are the results for', results_title)


class CreateQuestionListTest(FunctionalTestsBase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def test_can_create_a_question_list(self):
        # javi goes the the section where she can create a question list
        self.sign_up('javi@email.com', 'super_password_123')
        self.browser.get(f'{self.live_server_url}/lists/create/')

        # There is a title that invites her to create a question list
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Create a question list', title)

        # She fill the form and create a question list
        title_input = self.browser.find_element_by_id('id_title')
        title_input.send_keys('An amazing list')
        self.browser.find_element_by_tag_name('button').click()

        # Check that the question list got created
        last_list = QuestionList.objects.last()
        self.assertEqual(last_list.__str__(), 'An amazing list')
        # Check that the url changed, to something related to add a question
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/an-amazing-list/add_question/',
        )

        # There is a title that invites her to create a question
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Create a question', title)

        # She fill the form and create a question
        title_input = self.browser.find_element_by_id('id_title')
        title_input.send_keys('Is this actually working?')
        self.browser.find_element_by_tag_name('button').click()

        # There is a title that invites her to add alternatives to the question
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Add alternatives', title)

        # She fill the form and create a two alternatives
        title_input = self.browser.find_element_by_id('id_alternative_1')
        title_input.send_keys('Yes, is working')
        title_input = self.browser.find_element_by_id('id_alternative_2')
        title_input.send_keys('No, is not working')
        self.browser.find_element_by_tag_name('button').click()

        # Check that the url changed, to something related to add a question
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/an-amazing-list/add_question/',
        )

        # Check that she is the owner of the question list
        self.assertEqual('javi', last_list.owner.username)
        # Check that the list is not activated yet
        self.assertFalse(last_list.active)

        # She presses the "complete list" button
        complete_button = self.browser.find_element_by_id('complete_button')
        complete_button.click()
        # Check that the list activated
        last_list = QuestionList.activated_lists.last()
        self.assertTrue(last_list.active)

    def test_only_active_list_are_shown(self):
        # 2 question lists are created
        question_list = QuestionListFactory(title='awesome list')
        QuestionListFactory(title='normal list')
        # 1 of them is activated
        question_list.activate()
        question_list.save()

        # Javi goes to the lists view
        self.sign_up('javi@email.com', 'super_password_123')
        self.browser.get(f'{self.live_server_url}/lists/')

        # She only sees one of the lists (the activated one)
        html_ul_list = self.browser.find_element_by_tag_name('ul').text
        self.assertIn('awesome list', html_ul_list)
        self.assertNotIn('normal list', html_ul_list)

    def test_attempt_to_complete_a_list_with_no_full_question(self):
        # javi goes the the section where she can add questions to a list
        self.sign_up('javi@email.com', 'super_password_123')
        QuestionListFactory(title='awesome list')
        self.browser.get(
            f'{self.live_server_url}/lists/awesome-list/add_question/'
        )

        # She presses the "complete list" button
        complete_button = self.browser.find_element_by_id('complete_button')
        complete_button.click()

        # She is redirected to the same url but with an error message
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/awesome-list/add_question/',
        )

        error_message = self.browser.find_element_by_id('messages').text

        self.assertIn(LIST_COMPLETION_ERROR_MESSAGE, error_message)

    def test_attempt_to_access_an_incomplete_list(self):
        # Javi attemps to visits an incomplete list view
        self.sign_up('javi@email.com', 'super_password_123')
        QuestionListFactory(title='incomplete list')
        self.browser.get(
            f'{self.live_server_url}/lists/incomplete-list/'
            )

        # She is redirected to the lists view
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/',
        )


class UserProfileTests(FunctionalTestsBase):
    def setUp(self):
        self.browser = webdriver.Firefox()

    def test_user_activate_a_list(self):
        # Javi goes the the section where she can all her lists
        self.sign_up('javi@email.com', 'super_password_123')
        self.browser.get(
            f'{self.live_server_url}/users/javi/lists/'
        )

        # There is a message welcoming her to her lists
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('These are your lists', title)
