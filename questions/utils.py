import random

from .models import Question


def get_random_question_for_user(user):
    possible_questions = get_possible_questions_for_user(user)
    random_number = random.randrange(len(possible_questions))
    return possible_questions[random_number]


def get_possible_questions_for_user(user):
    all_questions = Question.objects.all()
    possible_questions = [
        question
        for question in all_questions
        if question.has_the_user_already_voted(user) is False
    ]
    return possible_questions
