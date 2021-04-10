from pathlib import Path

from django.conf import settings
from django.utils.translation import gettext_lazy as _

# === Global variables ===
AMOUNT_OF_LISTS_PER_PAGE = 6
AMOUNT_OF_DAYS_FOR_POPULARITY = 10
MAX_IMAGE_SIZE = 2 * 1000 * 1000
IMAGE_VALID_EXTENSIONS = ['.jpg', '.jpeg', '.png']
DEFAULT_IMAGE_NAME = 'default_alternative.jpg'

# === Flash Messages ===
LIST_COMPLETION_ERROR_MESSAGE = _(
    'The list needs at least 1 question with 2 alternatives to be completed'
)
ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE = _(
    'The list you are trying to see is incomplete'
)
LIST_CREATED_SUCCESSFULLY = _('List was created successfully')
LIST_EDITED_SUCCESSFULLY = _('List was edited successfully')
LIST_DELETED_SUCCESSFULLY = _('List was deleted successfully')
LIST_PUBLISHED_SUCCESSFULLY = _('List was published successfully')
LIST_REACHED_MAXIMUM_OF_QUESTION = _('The list reached the limit of questions')
QUESTION_CREATED_SUCCESSFULLY = _('Question was created successfully')
QUESTION_EDITED_SUCCESSFULLY = _('Question was edited successfully')
QUESTION_DELETED_SUCCESSFULLY = _('Question was deleted successfully')
ALREADY_ANSWERED_ALL_THE_QUESTIONS = _(
    'You already answered all the questions for this list'
)
MUST_COMPLETE_LIST_BEFORE_SEING_RESULTS = _(
    'You must answer all the list questions before seeing its results'
)
USER_THAT_SHARED_LIST_HAVENT_COMPLETED_IT = _(
    "The user that shared this list with you haven't answer all its "
    "questions, so you won't be able to see that person answers. Tell the "
    "user to answer all the questions"
)
DONT_TRY_WEIRD_STUFF = _('Please do not try to do weird stuff with the site')

# === Related to forms ===
# Errors
SPECIAL_CHARS_ERROR = _('Do not use special chars.')
# Note: related to MAX_IMAGE_SIZE
FILE_TOO_LARGE_ERROR = _('File too large. Size should not exceed 2 MB.')
# Note: related to IMAGE_VALID_EXTENSIONS
FILE_EXTENSION_ERROR = _(
    'File extension not valid. Allowed extensions: .jpg, .jpeg, .png.'
)

# Help text
MAX_AND_MIN_LENGTH = _(
    "100 characters max and 5 min. Also don't use special chars."
)
MAX_AND_SPECIAL_CHARS = _("100 characters max. Also don't use special chars.")
INVALID_HEADER_ON_EMAIL = _('Invalid header found.')
# Note: related to MAX_IMAGE_SIZE
FILE_TOO_LARGE_HELPER = _('Picture must have a size under 2 MB.')

# === Tests ===
TEST_FOLDER_TO_STORE_IMAGES = Path('for_tests')
COMPLETE_PATH_TO_TEST_IMGS_FOLDER = (
    settings.MEDIA_ROOT / 'alternative_pics' / TEST_FOLDER_TO_STORE_IMAGES
)

# === Commands ===
# delete_test_images_folder
COMMAND_ERROR_MESSAGE = (
    'Path does not exist: %s' % COMPLETE_PATH_TO_TEST_IMGS_FOLDER
)
COMMAND_HELP_TEXT = 'Delete the folder used by tests to store images'
COMMAND_SUCCESS_MESSAGE = (
    'Path was deleted: %s' % COMPLETE_PATH_TO_TEST_IMGS_FOLDER
)
