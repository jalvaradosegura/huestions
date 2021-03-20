from django.utils.translation import gettext_lazy as _

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
