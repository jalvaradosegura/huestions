import time

from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase

from allauth.account.models import EmailAddress
from selenium import webdriver

from lists.factories import QuestionListFactory
from lists.models import QuestionList
from core.constants import (
    ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE,
    LIST_COMPLETION_ERROR_MESSAGE,
    LIST_CREATED_SUCCESSFULLY,
    LIST_DELETED_SUCCESSFULLY,
    LIST_EDITED_SUCCESSFULLY,
    LIST_PUBLISHED_SUCCESSFULLY,
    QUESTION_CREATED_SUCCESSFULLY,
    QUESTION_DELETED_SUCCESSFULLY,
    QUESTION_EDITED_SUCCESSFULLY,
)
from questions.factories import AlternativeFactory, QuestionFactory
from votes.models import Vote


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
        self.browser.find_element_by_id('sign_up_button').click()

        # Verify the user
        email_address = EmailAddress.objects.get(email=email)
        email_address.verified = True
        email_address.save()


class NewVisitorTests(FunctionalTestsBase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.sign_up('javi@email.com', 'super_password_123')

    def test_can_visit_home_page(self):
        # Javi heard about a fun page, where you have to answer hard questions
        # She visits it
        self.browser.get(f'{self.live_server_url}/')

        # Javi sees a Home Page title
        welcome = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual(welcome, 'Home Page')


class QuestionListsTests(FunctionalTestsBase):
    def setUp(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('intl.accept_languages', 'en')
        self.browser = webdriver.Firefox(firefox_profile=profile)

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

    def test_can_visit_a_list_of_question_page_and_vote(self):
        # Javi visits a page that show a list of list questions
        self.browser.get(f'{self.live_server_url}/lists/')

        time.sleep(3)
        # She sees a big title that says something abouth the lists
        title = self.browser.find_element_by_tag_name('h2').text
        self.assertIn('Lists', title)

        # She selects the first list
        button_to_select = self.browser.find_element_by_id('button_to_select')
        button_to_select.click()

        # She sees the question title in the new url
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/some-cool-title/',
        )

        # She answer the first question
        vote_for_an_alternative(self.browser, 'id_alternatives_0')
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/some-cool-title/',
        )

        # She answer the next question
        vote_for_an_alternative(self.browser, 'id_alternatives_0')

        # Check that a vote record got created
        vote = Vote.objects.last()
        self.assertEqual(vote.list.__str__(), 'some cool title')


class CreateListTests(FunctionalTestsBase):
    def setUp(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('intl.accept_languages', 'en')
        self.browser = webdriver.Firefox(firefox_profile=profile)

    def test_can_create_a_question_list(self):
        # javi goes the the section where she can create a question list
        self.sign_up('javi@email.com', 'super_password_123')
        self.browser.get(f'{self.live_server_url}/lists/create/')

        # There is a title that invites her to create a question list
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Create', title)

        # She fill the form and create a question list
        title_input = self.browser.find_element_by_id('id_title')
        title_input.send_keys('An amazing list')
        self.browser.find_element_by_id('create_list_button').click()

        # Check for flash message
        message = self.browser.find_element_by_class_name('alert').text
        self.assertIn(str(LIST_CREATED_SUCCESSFULLY), message)

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
        alternative_1_input = self.browser.find_element_by_id(
            'id_alternative_1'
        )
        alternative_2_input = self.browser.find_element_by_id(
            'id_alternative_2'
        )
        title_input.send_keys('Is this actually working?')
        alternative_1_input.send_keys('yes')
        alternative_2_input.send_keys('no')
        create_question_button = self.browser.find_element_by_id(
            'create_question_and_add_another_button'
        )
        create_question_button.click()

        # Check for flash message
        message = self.browser.find_element_by_class_name('alert').text
        self.assertIn(str(QUESTION_CREATED_SUCCESSFULLY), message)

        # She is redirected to the same page
        self.assertIn('Create a question', title)
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/an-amazing-list/add_question/',
        )

        # Check that she is the owner of the question list
        self.assertEqual('javi', last_list.owner.username)
        # Check that the list is not activated yet
        self.assertFalse(last_list.active)

        # She fill the form again and create a question & publish the list
        title_input = self.browser.find_element_by_id('id_title')
        alternative_1_input = self.browser.find_element_by_id(
            'id_alternative_1'
        )
        alternative_2_input = self.browser.find_element_by_id(
            'id_alternative_2'
        )
        title_input.send_keys('Is this actually working?')
        alternative_1_input.send_keys('yes')
        alternative_2_input.send_keys('no')
        create_question_button = self.browser.find_element_by_id(
            'create_question_and_publish'
        )
        create_question_button.click()

        # Check that the list activated
        last_list = QuestionList.activated_lists.last()
        self.assertTrue(last_list.active)

        # Check that the list has the question and the latter the alternatives
        question = last_list.questions.last()
        alternative_1 = question.alternatives.first()
        alternative_2 = question.alternatives.last()
        self.assertEqual(question.title, 'Is this actually working?')
        self.assertEqual(alternative_1.title, 'Yes')
        self.assertEqual(alternative_2.title, 'No')

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
        html_ul_list = self.browser.find_element_by_class_name(
            'container'
        ).text
        self.assertIn('awesome list', html_ul_list)
        self.assertNotIn('normal list', html_ul_list)

    def test_attempt_to_access_an_incomplete_list(self):
        # Javi attemps to visits an incomplete list view
        self.sign_up('javi@email.com', 'super_password_123')
        QuestionListFactory(title='incomplete list')
        self.browser.get(f'{self.live_server_url}/lists/incomplete-list/')

        # She is redirected to the lists view
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/',
        )

        # She sees a message, it says she is attempting to see an incomplete
        # view
        error_message = self.browser.find_element_by_class_name('alert').text

        self.assertIn(
            str(ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE), error_message
        )


class UserProfileTests(FunctionalTestsBase):
    def setUp(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('intl.accept_languages', 'en')
        self.browser = webdriver.Firefox(firefox_profile=profile)

    def test_user_publish_a_list(self):
        # Set up a list for Javi
        self.sign_up('javi@email.com', 'super_password_123')
        user = get_user_model().objects.get(email='javi@email.com')
        question_list = QuestionListFactory(title='my first list', owner=user)

        # Add a question to the lists
        question = QuestionFactory(
            title='is this cool?', child_of=question_list
        )
        QuestionFactory(title='is this awesome?', child_of=question_list)

        # Add alternatives to the same list
        AlternativeFactory(title='Yes', question=question)
        AlternativeFactory(title='No', question=question)

        # Javi goes the the section where she can see all her lists
        self.browser.get(f'{self.live_server_url}/users/javi/lists/')

        # There is a message welcoming her to her lists
        title = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('Your lists', title)

        # She tries to edit one of the lists
        self.browser.find_element_by_id('edit_0').click()
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/my-first-list/edit/',
        )

        # There is a form inviting here to change the title of the list
        title_input = self.browser.find_element_by_id('id_title')

        # Check for the text of the input of the list title
        self.assertEqual(title_input.get_attribute('value'), 'my first list')

        # She writes a new title for the list
        title_input.clear()
        title_input.send_keys('new name for my list')
        self.browser.find_element_by_id('edit_list_button').click()

        # Check for flash message
        message = self.browser.find_element_by_class_name('alert').text
        self.assertIn(str(LIST_EDITED_SUCCESSFULLY), message)

        # Check she is back to her lists
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/users/javi/lists/',
        )

        # Check that the list has the new name
        lists = self.browser.find_element_by_tag_name('h5').text
        self.assertIn('new name for my list', lists)

        # She tries to edit the same list again
        self.browser.find_element_by_id('edit_0').click()
        # Check that the url has the new name
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/new-name-for-my-list/edit/',
        )

        # She realizes that below the input for the list name, there is a list
        # with the questions that belong to the list
        questions = self.browser.find_element_by_id('question_0_title').text
        self.assertIn('is this cool', questions)

        # There is a button for editing each question, she presses the first
        # one
        self.browser.find_element_by_id('edit_question_0').click()
        # She is now on a url for editing the question with its alternatives
        self.assertEqual(
            self.browser.current_url,
            (
                f'{self.live_server_url}/lists/new-name-for-my-list/'
                f'{question.slug}/{question.id}/edit/'
            ),
        )

        # There is a form for editing the question and its alternatives
        question_title = self.browser.find_element_by_id('id_title')
        alternative_1 = self.browser.find_element_by_id('id_alternative_1')
        alternative_2 = self.browser.find_element_by_id('id_alternative_2')

        # She writes some new info
        question_title.clear()
        alternative_1.clear()
        alternative_2.clear()
        question_title.send_keys("This was edited?")
        alternative_1.send_keys("Yes it was")
        alternative_2.send_keys("No it was not")
        self.browser.find_element_by_id('edit_question_button').click()

        # Check for flash message
        message = self.browser.find_element_by_class_name('alert').text
        self.assertIn(str(QUESTION_EDITED_SUCCESSFULLY), message)

        # She is back to the edit list view
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/new-name-for-my-list/edit/',
        )

        # She tries to edit the same question again
        self.browser.find_element_by_id('edit_question_0').click()
        # The url has the new name now
        self.assertEqual(
            self.browser.current_url,
            (
                f'{self.live_server_url}/lists/new-name-for-my-list/'
                f'this-was-edited/{question.id}/edit/'
            ),
        )

        # She goes back to the edit list view with the intention of
        # completing it
        self.browser.get(
            f'{self.live_server_url}/lists/new-name-for-my-list/edit/'
        )
        complete_button = self.browser.find_element_by_id('complete_button')
        complete_button.click()

        # Check for flash message
        message = self.browser.find_element_by_class_name('alert').text
        self.assertIn(str(LIST_PUBLISHED_SUCCESSFULLY), message)

        # She is back to her lists after clicking it
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/users/javi/lists/',
        )

    def test_user_try_to_publish_an_incomplete_list(self):
        # Set up a list for Javi
        self.sign_up('javi@email.com', 'super_password_123')
        user = get_user_model().objects.get(email='javi@email.com')
        question_list = QuestionListFactory(title='my first list', owner=user)

        # Add a questions to the lists
        QuestionFactory(title='is this cool?', child_of=question_list)

        # She goes to the the edit list view and try to complete it
        self.browser.get(f'{self.live_server_url}/lists/my-first-list/edit/')
        complete_button = self.browser.find_element_by_id('complete_button')
        complete_button.click()
        # She is still in the same page because the list is not completed
        # It needs at least 1 question with 2 alternatives
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/my-first-list/edit/',
        )
        error_message = self.browser.find_element_by_class_name('alert').text
        self.assertIn(str(LIST_COMPLETION_ERROR_MESSAGE), error_message)

    def test_user_delete_a_list(self):
        # Set up a list for Javi
        self.sign_up('javi@email.com', 'super_password_123')
        user = get_user_model().objects.get(email='javi@email.com')
        QuestionListFactory(title='my first list', owner=user)

        # She goes  to see her lists
        self.browser.get(f'{self.live_server_url}/users/javi/lists/')

        # She press the button to delete the question
        self.browser.find_element_by_id('delete_0').click()

        # She is redirected to a view for confirming the deletion
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/my-first-list/delete/',
        )

        # There is a confirmation form, she presses the delete button
        self.browser.find_element_by_id('delete_button').click()

        # Check for flash message
        message = self.browser.find_element_by_class_name('alert').text
        self.assertIn(str(LIST_DELETED_SUCCESSFULLY), message)

        # She is redirected to her lists
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/users/javi/lists/',
        )

    def test_user_delete_a_question_from_a_list(self):
        # Set up a list for Javi
        self.sign_up('javi@email.com', 'super_password_123')
        user = get_user_model().objects.get(email='javi@email.com')
        question_list = QuestionListFactory(title='a list', owner=user)
        QuestionFactory(title='is this cool?', child_of=question_list)

        # She goes to see the details of the list
        self.browser.get(f'{self.live_server_url}/lists/a-list/edit/')

        # She press the button to delete the question
        self.browser.find_element_by_id('delete_0').click()

        # Check for flash message
        message = self.browser.find_element_by_class_name('alert').text
        self.assertIn(str(QUESTION_DELETED_SUCCESSFULLY), message)

        # She is redirected to the same edit list view
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/a-list/edit/',
        )

    def test_user_navigates_from_edit_list_to_add_question_then_return(self):
        # Set up a list for Javi
        self.sign_up('javi@email.com', 'super_password_123')
        user = get_user_model().objects.get(email='javi@email.com')
        question_list = QuestionListFactory(title='a list', owner=user)

        # She goes to see her list
        self.browser.get(
            f'{self.live_server_url}/lists/{question_list.slug}/edit/'
        )
        # She press the button to add a question
        self.browser.find_element_by_id('add_question').click()

        # She is sent to the add question view
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/{question_list.slug}/add_question/',
        )

        # She press the button to go back to the list
        self.browser.find_element_by_id('view_list').click()

        # She is sent back to her list
        self.assertEqual(
            self.browser.current_url,
            f'{self.live_server_url}/lists/{question_list.slug}/edit/',
        )

    def test_users_can_see_their_stats(self):
        # Set up a few lists for Javi
        self.sign_up('javi@email.com', 'super_password_123')
        user = get_user_model().objects.get(email='javi@email.com')
        QuestionListFactory(title='list 1', owner=user)
        QuestionListFactory(title='list 2', owner=user)
        QuestionListFactory(title='list 3', owner=user)
        QuestionListFactory(title='list 4', owner=user)
        AlternativeFactory().vote_for_this_alternative(user)
        AlternativeFactory().vote_for_this_alternative(user)
        AlternativeFactory().vote_for_this_alternative(user)

        # She goes to see her stats
        self.browser.get(
            f'{self.live_server_url}/users/{user.username}/stats/'
        )
        body = self.browser.find_element_by_tag_name('body').text

        # There is a 4 within the body of the page, indicating that she has
        # created 4 lists
        self.assertIn('4', body)
        # There is a 3 within the body of the page, indicating that she has
        # answered 3 questions
        self.assertIn('3', body)
