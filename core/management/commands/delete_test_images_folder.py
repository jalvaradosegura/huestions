import shutil

from django.core.management.base import BaseCommand, CommandError

from core.constants import (
    COMMAND_ERROR_MESSAGE,
    COMMAND_HELP_TEXT,
    COMMAND_SUCCESS_MESSAGE,
    COMPLETE_PATH_TO_TEST_IMGS_FOLDER,
)


class Command(BaseCommand):
    help = COMMAND_HELP_TEXT

    def handle(self, *args, **options):
        try:
            shutil.rmtree(COMPLETE_PATH_TO_TEST_IMGS_FOLDER)
        except FileNotFoundError:
            raise CommandError(COMMAND_ERROR_MESSAGE)

        self.stdout.write(self.style.SUCCESS(COMMAND_SUCCESS_MESSAGE))
