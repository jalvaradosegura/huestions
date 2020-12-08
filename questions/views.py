from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


from .models import Question, Alternative
from .utils import get_random_question_for_user


@login_required
def home(request):
    if request.method == 'POST':
        question_id = request.POST['question_id']
        chosen_alternative = Alternative.objects.get(
            id=request.POST['alternative']
        )
        user = request.user
        chosen_alternative.users.add(user)

        return redirect('details', question_id=question_id)
    last_question = Question.objects.last()
    already_voted = last_question.has_the_user_already_voted(request.user)
    return render(
        request,
        'home.html',
        {
            'question': last_question,
            'alread_voted': already_voted,
            'title': 'Huestion'
        },
    )


def details(request, question_id):
    question = Question.objects.get(id=question_id)
    return render(request, 'details.html', {'question': question})


def random_question(request):
    question = get_random_question_for_user(request.user)
    return render(
        request,
        'home.html',
        {'question': question, 'title': 'Random Huestion'},
    )
