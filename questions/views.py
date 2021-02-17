from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, reverse
from django.views.generic import DetailView, ListView

from .constants import LIST_COMPLETION_ERROR_MESSAGE
from .forms import (
    AddAlternativesForm,
    AnswerQuestionForm,
    CompleteListForm,
    CreateQuestionForm,
    CreateQuestionListForm
)
from .models import Alternative, Question, QuestionList
from .utils import get_random_question_for_user


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
            'title': 'Huestion',
        },
    )


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
            'title': 'Random Huestion',
        },
    )


class QuestionsListView(LoginRequiredMixin, ListView):
    queryset = QuestionList.activated_lists.all()
    template_name = 'question_list.html'


class AnswerQuestionListView(LoginRequiredMixin, DetailView):
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

        context['already_voted'] = Question.objects.get(
            id=question_id
        ).has_the_user_already_voted(self.request.user)

        return context

    def post(self, request, *args, **kwargs):
        selected_alternative = Alternative.objects.get(
            id=request.POST['alternatives']
        )
        if not selected_alternative.question.has_the_user_already_voted(
            self.request.user
        ):
            selected_alternative.vote_for_this_alternative(self.request.user)

        question_list = QuestionList.objects.get(
            id=request.POST['question_list_id']
        )

        if 'next_page' in request.POST:
            next_page = request.POST['next_page']
            return redirect(
                reverse(
                    'questions_list_details',
                    kwargs={'slug': question_list.slug},
                )
                + f'?page={next_page}'
            )
        return redirect(
            'questions_list_details_results', slug=question_list.slug
        )


class QuestionListResultsView(LoginRequiredMixin, DetailView):
    model = QuestionList
    template_name = 'question_list_details_results.html'


@login_required
def create_question_list(request):
    if request.method == 'POST':
        form = CreateQuestionListForm(request.POST, owner=request.user)

        if form.is_valid():
            question_list = form.save(commit=False)
            question_list.save()
            return redirect('create_question', question_list.slug)

    form = CreateQuestionListForm(owner=request.user)
    return render(request, 'create_question_list.html', {'form': form})


@login_required
def create_question(request, list_slug):
    question_list = QuestionList.objects.get(slug=list_slug)
    form = CreateQuestionForm(question_list=question_list)
    complete_list_form = CompleteListForm(question_list=question_list)

    if request.method == 'POST':
        if 'title' not in request.POST:
            if complete_list_form.is_valid():
                complete_list_form.save()
                return redirect('questions_list')
            messages.add_message(
                request,
                messages.ERROR,
                complete_list_form.custom_error_message
            )
        form = CreateQuestionForm(request.POST, question_list=question_list)
        if form.is_valid():
            question = form.save(commit=False)
            question.save()
            return redirect(
                'add_alternatives',
                question_list.slug,
                question.slug,
                question.id
            )

    return render(
        request,
        'create_question.html',
        {'form': form, 'complete_list_form': complete_list_form}
    )


@login_required
def add_alternatives(request, list_slug, question_slug, question_id):
    question = Question.objects.get(id=question_id)
    form = AddAlternativesForm(question=question)

    if request.method == 'POST':
        form = AddAlternativesForm(request.POST, question=question)

        if form.is_valid():
            form.save()
            question_list = question.child_of
            return redirect('create_question', question_list.slug)

    return render(request, 'add_alternatives.html', {'form': form})
