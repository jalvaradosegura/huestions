from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView

from .models import Alternative, Question, QuestionList
from .utils import get_random_question_for_user
from .forms import AnswerQuestionForm


@login_required
def home(request):
    if request.method == 'POST':
        chosen_alternative = Alternative.objects.get(
            id=request.POST['alternative']
        )
        user = request.user
        chosen_alternative.users.add(user)
        question = Question.objects.get(id=request.POST['question_id'])
        return redirect(question)

    last_question = Question.objects.last()
    already_voted = last_question.has_the_user_already_voted(request.user)
    return render(
        request,
        'home.html',
        {
            'question': last_question,
            'alread_voted': already_voted,
            'title': 'Huestion'
        },)


@login_required
def details(request, question_id):
    question = Question.objects.get(id=question_id)
    return render(request, 'details.html', {'question': question})


@login_required
def random_question(request):
    if request.method == 'POST':
        chosen_alternative = Alternative.objects.get(
            id=request.POST['alternative']
        )
        user = request.user
        chosen_alternative.users.add(user)
        question = Question.objects.get(id=request.POST['question_id'])
        return redirect(question)

    question = get_random_question_for_user(request.user)
    already_voted = True if question is None else False

    return render(
        request,
        'home.html',
        {
            'question': question,
            'alread_voted': already_voted,
            'title': 'Random Huestion'
        },
    )


class QuestionsListListView(ListView):
    model = QuestionList
    template_name = 'question_list.html'


class QuestionsListDetailView(DetailView):
    model = QuestionList
    template_name = 'question_list_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions_list = self.get_object().questions.all().order_by('id')
        paginator = Paginator(questions_list, 1)

        page = self.request.GET.get('page')

        context['questions'] = paginator.get_page(page)

        question_id = [question.id for question in context['questions']][0]
        context['form'] = AnswerQuestionForm(question_id)

        return context

    def post(self, request, *args, **kwargs):
        return redirect('home')
