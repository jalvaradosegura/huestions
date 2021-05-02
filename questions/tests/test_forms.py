from http import HTTPStatus
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from core.constants import (
    DEFAULT_IMAGE_NAME,
    FILE_EXTENSION_ERROR,
    FILE_TOO_LARGE_ERROR,
    LIST_REACHED_MAXIMUM_OF_QUESTION,
    SPECIAL_CHARS_ERROR,
)
from core.mixins import LoginUserMixin

from ..factories import (
    AlternativeFactory,
    QuestionFactory,
    QuestionListFactory,
)
from ..forms import AddAlternativesForm, AnswerQuestionForm, CreateQuestionForm
from ..models import Alternative, Question
from ..utils import create_an_img_ready_for_models


class AnswerQuestionFormTests(TestCase):
    def test_generate_the_form_with_choices(self):
        question = QuestionFactory(title='What is this question')
        alternative_1 = AlternativeFactory(title='a1', question=question)
        alternative_2 = AlternativeFactory(title='a2', question=question)

        form = AnswerQuestionForm(question.id)

        self.assertEqual(
            alternative_1.__str__(), form.fields['alternatives'].choices[0][1]
        )
        self.assertEqual(
            alternative_2.__str__(), form.fields['alternatives'].choices[1][1]
        )


class AnswerQuestionFormViewTests(LoginUserMixin, TestCase):
    def test_get_success(self):
        question_list = QuestionListFactory(title='awesome list', active=True)
        question = QuestionFactory(
            title='awesome question', child_of=question_list
        )
        AlternativeFactory(title='awesome alternative 1', question=question)
        AlternativeFactory(title='awesome alternative 2', question=question)
        self.create_login_and_verify_user()

        response = self.client.get(
            reverse('answer_list', args=[question_list.slug])
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'id="id_alternatives_0"')
        self.assertContains(response, 'id="id_alternatives_1"')

    def test_post_success_and_adds_user_to_alternative(self):
        question_list = QuestionListFactory(title='awesome list')

        question = QuestionFactory(
            title='awesome question', child_of=question_list
        )
        another_question = QuestionFactory(
            title='another awesome question', child_of=question_list
        )
        alternative = AlternativeFactory(
            title='awesome alternative', question=question
        )
        AlternativeFactory(
            title='another alternative', question=another_question
        )
        self.create_login_and_verify_user()

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug]),
            data={
                'alternatives': [alternative.id],
                'list_slug': question_list.slug,
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('answer_list', args=[question_list.slug]),
        )
        self.assertEqual(self.user.alternatives_chosen.count(), 1)

    def test_post_and_go_to_results(self):
        question_list = QuestionListFactory(title='awesome list')
        question = QuestionFactory(
            title='awesome question', child_of=question_list
        )
        alternative = AlternativeFactory(
            title='awesome alternative', question=question
        )
        self.create_login_and_verify_user()

        response = self.client.post(
            reverse('answer_list', args=[question_list.slug]),
            data={
                'alternatives': [alternative.id],
                'list_slug': question_list.slug,
            },
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            response['Location'],
            reverse('list_results', args=[question_list.slug]),
        )
        self.assertEqual(self.user.alternatives_chosen.count(), 1)


class CreateQuestionFormTests(LoginUserMixin, TestCase):
    def test_get_form_success(self):
        self.create_login_and_verify_user()
        question_list = QuestionListFactory(
            title='an awesome list', owner=self.user
        )

        response = self.client.get(
            reverse('add_question', args=[question_list.slug])
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, '<input type="text" name="title"')

    def test_create_question_with_form(self):
        question_list = QuestionListFactory(title='an awesome list')

        form = CreateQuestionForm(
            data={'title': 'Is this working??'}, question_list=question_list
        )
        form.save()
        question = Question.objects.last()

        self.assertEqual(question.__str__(), 'Is this working??')
        self.assertEqual(Question.objects.all().count(), 1)

    def test_create_question_without_question_mark(self):
        question_list = QuestionListFactory(title='an awesome list')

        form = CreateQuestionForm(
            data={'title': 'Who is better'}, question_list=question_list
        )
        form.save()
        question = Question.objects.last()

        self.assertEqual(question.__str__(), 'Who is better')
        self.assertEqual(Question.objects.all().count(), 1)

    def test_list_reached_the_limit_of_questions(self):
        question_list = QuestionListFactory(title='an awesome list')
        QuestionFactory(title='a', child_of=question_list)
        QuestionFactory(title='a', child_of=question_list)
        QuestionFactory(title='a', child_of=question_list)

        form = CreateQuestionForm(
            data={'title': 'Who is better'}, question_list=question_list
        )
        form.questions_amount_limit = 3
        response = form.is_valid()

        self.assertFalse(response)
        self.assertIn(LIST_REACHED_MAXIMUM_OF_QUESTION, form.errors['__all__'])

    def test_create_question_with_special_chars_on_title(self):
        question_list = QuestionListFactory(title='an awesome list')

        form = CreateQuestionForm(
            data={
                'title': 'emoji 😁',
            },
            question_list=question_list,
        )

        self.assertIn(SPECIAL_CHARS_ERROR, form.errors['title'])

    def test_create_question_title_is_too_short(self):
        question_list = QuestionListFactory(title='an awesome list')

        form = CreateQuestionForm(
            data={
                'title': 'abc',
            },
            question_list=question_list,
        )

        self.assertIn(
            'Ensure this value has at least', form.errors['title'][0]
        )


class AddAlternativesFormTests(LoginUserMixin, TestCase):
    NAME_FOR_IMAGE_1 = 'IFT1_image_for_testing_123.jpg'
    NAME_FOR_IMAGE_2 = 'IFT2_image_for_testing_223.jpg'

    def setUp(self):
        self.question_list = QuestionListFactory(title='an awesome list')
        self.question = QuestionFactory(
            title='Is this hard?', child_of=self.question_list
        )
        image_1 = Path(
            settings.MEDIA_ROOT / 'alternative_pics' / self.NAME_FOR_IMAGE_1
        )
        image_2 = Path(
            settings.MEDIA_ROOT / 'alternative_pics' / self.NAME_FOR_IMAGE_2
        )
        if image_1.is_file():
            image_1.unlink()
        if image_2.is_file():
            image_2.unlink()

    def test_get_form_success(self):
        self.create_login_and_verify_user()
        question_list = QuestionListFactory(title='cool list', owner=self.user)

        response = self.client.get(
            reverse('add_question', args=[question_list.slug])
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'name="alternative_1"')
        self.assertContains(response, 'name="alternative_2"')

    def test_add_alternatives_with_form(self):
        form = AddAlternativesForm(
            data={
                'alternative_1': 'Yes it is',
                'alternative_2': 'No it is not',
            }
        )

        if form.is_valid():
            form.save(question=self.question)
        firt_alternative = Alternative.objects.first()
        last_alternative = Alternative.objects.last()

        self.assertEqual(firt_alternative.__str__(), 'Yes it is')
        self.assertEqual(last_alternative.__str__(), 'No it is not')
        self.assertEqual(firt_alternative.question.__str__(), 'Is this hard?')
        self.assertEqual(last_alternative.question.__str__(), 'Is this hard?')
        self.assertEqual(Alternative.objects.all().count(), 2)

    def test_add_alternatives_with_form_having_question_marks(self):
        form = AddAlternativesForm(
            data={
                'alternative_1': '?yes it is?',
                'alternative_2': 'acción',
            }
        )

        if form.is_valid():
            form.save(question=self.question)
        firt_alternative = Alternative.objects.first()
        last_alternative = Alternative.objects.last()

        self.assertEqual(firt_alternative.__str__(), '?yes it is?')
        self.assertEqual(last_alternative.__str__(), 'Acción')
        self.assertEqual(Alternative.objects.all().count(), 2)

    def test_add_alternatives_and_attributions_with_form(self):
        form = AddAlternativesForm(
            data={
                'alternative_1': '?yes it is?',
                'alternative_2': 'acción',
                'attribution_1': 'some credit',
                'attribution_2': 'another credit',
            }
        )

        if form.is_valid():
            form.save(question=self.question)
        firt_alternative = Alternative.objects.first()
        last_alternative = Alternative.objects.last()

        self.assertEqual(firt_alternative.__str__(), '?yes it is?')
        self.assertEqual(firt_alternative.attribution, 'some credit')
        self.assertEqual(last_alternative.__str__(), 'Acción')
        self.assertEqual(last_alternative.attribution, 'another credit')
        self.assertEqual(Alternative.objects.all().count(), 2)

    def test_alternatives_all_in_lower_case(self):
        self.create_login_and_verify_user()
        form = AddAlternativesForm(
            data={'alternative_1': 'yes', 'alternative_2': 'no'},
        )

        if form.is_valid():
            form.save(question=self.question)
        firt_alternative = Alternative.objects.first()
        last_alternative = Alternative.objects.last()

        self.assertEqual(firt_alternative.__str__(), 'Yes')
        self.assertEqual(last_alternative.__str__(), 'No')

    def test_create_alternatives_with_special_chars_on_title(self):
        form = AddAlternativesForm(
            data={
                'alternative_1': 'Yes it is 😁',
                'alternative_2': 'No it is not 😁',
            }
        )

        self.assertIn(SPECIAL_CHARS_ERROR, form.errors['alternative_1'])
        self.assertIn(SPECIAL_CHARS_ERROR, form.errors['alternative_2'])

    def test_add_alternatives_with_form_and_with_image(self):
        image_1 = create_an_img_ready_for_models(self.NAME_FOR_IMAGE_1)
        image_2 = create_an_img_ready_for_models(self.NAME_FOR_IMAGE_2)

        form = AddAlternativesForm(
            data={
                'alternative_1': 'Yes',
                'alternative_2': 'No',
            },
            files={'image_1': image_1, 'image_2': image_2},
        )
        if form.is_valid():
            form.save(question=self.question)

        firt_alternative = Alternative.objects.first()
        last_alternative = Alternative.objects.last()

        self.assertEqual(firt_alternative.__str__(), 'Yes')
        self.assertEqual(
            firt_alternative.image.name,
            f'alternative_pics/{self.NAME_FOR_IMAGE_1}',
        )
        self.assertEqual(last_alternative.__str__(), 'No')
        self.assertEqual(
            last_alternative.image.name,
            f'alternative_pics/{self.NAME_FOR_IMAGE_2}',
        )
        self.assertTrue(form.is_valid())

    def test_add_alternatives_with_form_alternative_2_no_image(self):
        image_1 = create_an_img_ready_for_models(self.NAME_FOR_IMAGE_1)

        form = AddAlternativesForm(
            data={
                'alternative_1': 'Yes',
                'alternative_2': 'No',
            },
            files={'image_1': image_1},
        )
        if form.is_valid():
            form.save(question=self.question)

        firt_alternative = Alternative.objects.first()
        last_alternative = Alternative.objects.last()

        self.assertEqual(firt_alternative.__str__(), 'Yes')
        self.assertEqual(
            firt_alternative.image.name,
            f'alternative_pics/{self.NAME_FOR_IMAGE_1}',
        )
        self.assertEqual(last_alternative.__str__(), 'No')
        self.assertEqual(
            last_alternative.image.name,
            DEFAULT_IMAGE_NAME,
        )
        self.assertTrue(form.is_valid())

    def test_add_alternatives_with_form_alternative_1_no_image(self):
        image_2 = create_an_img_ready_for_models(self.NAME_FOR_IMAGE_2)

        form = AddAlternativesForm(
            data={
                'alternative_1': 'Yes',
                'alternative_2': 'No',
            },
            files={'image_2': image_2},
        )
        if form.is_valid():
            form.save(question=self.question)

        firt_alternative = Alternative.objects.first()
        last_alternative = Alternative.objects.last()

        self.assertEqual(firt_alternative.__str__(), 'Yes')
        self.assertEqual(
            firt_alternative.image.name,
            DEFAULT_IMAGE_NAME,
        )
        self.assertEqual(last_alternative.__str__(), 'No')
        self.assertEqual(
            last_alternative.image.name,
            f'alternative_pics/{self.NAME_FOR_IMAGE_2}',
        )
        self.assertTrue(form.is_valid())

    @patch('questions.validators.MAX_IMAGE_SIZE', 0)
    def test_add_alternatives_with_form_with_image_too_big(self):
        image_1 = create_an_img_ready_for_models(self.NAME_FOR_IMAGE_1)

        form = AddAlternativesForm(
            data={
                'alternative_1': 'Yes',
                'alternative_2': 'No',
            },
            files={'image_1': image_1},
        )

        self.assertEqual(form.errors['image_1'], [FILE_TOO_LARGE_ERROR])

    @patch('questions.validators.IMAGE_VALID_EXTENSIONS', ['.png'])
    def test_add_alternatives_with_form_with_invalid_image_extension(self):
        image_1 = create_an_img_ready_for_models(self.NAME_FOR_IMAGE_1)

        form = AddAlternativesForm(
            data={
                'alternative_1': 'Yes',
                'alternative_2': 'No',
            },
            files={'image_1': image_1},
        )

        self.assertEqual(form.errors['image_1'], [FILE_EXTENSION_ERROR])
