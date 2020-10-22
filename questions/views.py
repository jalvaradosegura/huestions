from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import Question


def home(request):
    if request.method == 'POST':
        question_id = request.POST['question_id']
        return redirect('details', question_id=question_id)
    last_question = Question.objects.last()
    return render(request, 'home.html', {'last_question': last_question})


def details(request, question_id):
    question = Question.objects.get(id=question_id)
    return render(request, 'details.html', {'question': question})
