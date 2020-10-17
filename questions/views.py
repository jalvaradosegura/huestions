from django.shortcuts import render

from .models import Question


def home(request):
    last_question = Question.objects.last()
    return render(request, 'home.html', {'last_question': last_question})
