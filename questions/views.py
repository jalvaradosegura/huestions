from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

from .models import Question, Alternative


def home(request):
    if request.method == 'POST':
        question_id = request.POST['question_id']
        chosen_alternative = Alternative.objects.get(
            id=request.POST['alternative']
        )
        # TODO: Need to be changed to a real user
        user = get_user_model().objects.last()
        chosen_alternative.users.add(user)

        return redirect('details', question_id=question_id)
    last_question = Question.objects.last()
    return render(request, 'home.html', {'last_question': last_question})


def details(request, question_id):
    question = Question.objects.get(id=question_id)
    return render(request, 'details.html', {'question': question})
