from django.test import LiveServerTestCase

from selenium import webdriver


class NewVisitorTest(LiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_visit_home_page(self):
        # Javi heard about a fun page, where you have to answer hard questions
        # She visits it
        self.browser.get(self.live_server_url)

        # She notices the page title mention Huestion
        self.assertIn('Huestion', self.browser.title)

        # She is received with a question
        question = self.browser.find_element_by_tag_name('h1').text
        self.assertEqual('None', question)
