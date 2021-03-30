from django.test import TestCase

from ..forms import ContactForm


class ContactFormTests(TestCase):
    def test_create_question_with_special_chars_on_title(self):
        form = ContactForm(
            data={
                'from_email': 'invalid_email.com',
                'subject': 'bad email',
                'message': 'this should fail',
            }
        )

        self.assertIn(
            'Enter a valid email address.', form.errors['from_email']
        )
