from django.utils.translation import gettext_lazy as _

LIST_COMPLETION_ERROR_MESSAGE = (
    _('The list needs at least 1 question with 2 alternatives to be completed')
)
ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE = (
    _('The list you are trying to see is incomplete')
)
LIST_CREATED_SUCCESSFULLY = _('List was created successfully')
LIST_EDITED_SUCCESSFULLY = _('List was edited successfully')
LIST_DELETED_SUCCESSFULLY = _('List was deleted successfully')
LIST_PUBLISHED_SUCCESSFULLY = _('List was published successfully')
LIST_REACHED_MAXIMUM_OF_QUESTION = _('The list reached the limit of questions')
QUESTION_CREATED_SUCCESSFULLY = _('Question was created successfully')
QUESTION_EDITED_SUCCESSFULLY = _('Question was edited successfully')
QUESTION_DELETED_SUCCESSFULLY = _('Question was deleted successfully')
QUESTION_ALREADY_ANSWERED = (
    _("Question already answered. Your vote won't count this time.")
)
