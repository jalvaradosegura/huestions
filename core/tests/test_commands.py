import io
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from core.constants import (
    COMMAND_TEST_FOLDER_SUCCESS_MESSAGE,
    COMPLETE_PATH_TO_TEST_IMGS_FOLDER,
)


class DeleteTestImagesFolderCommandTests(TestCase):
    folder_path = Path(COMPLETE_PATH_TO_TEST_IMGS_FOLDER)

    def test_command_fail(self):
        self.folder_path.mkdir(parents=True, exist_ok=True)
        call_command('delete_test_images_folder')
        with self.assertRaises(CommandError):
            call_command('delete_test_images_folder')

    def test_command_success(self):
        self.folder_path.mkdir(parents=True, exist_ok=True)
        out = io.StringIO()
        call_command('delete_test_images_folder', stdout=out)
        self.assertIn(COMMAND_TEST_FOLDER_SUCCESS_MESSAGE, out.getvalue())
