from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, reverse
from django.views.generic import (
    DeleteView,
    DetailView,
    ListView,
    View,
    UpdateView,
)

from .constants import ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE
from .forms import (
    AddAlternativesForm,
    AnswerQuestionForm,
    CompleteListForm,
    CreateQuestionForm,
    CreateQuestionListForm,
    EditListForm,
)
from .models import Alternative, Question, QuestionList


@login_required
def home(request):
    return render(request, 'home.html')


class QuestionsListView(LoginRequiredMixin, ListView):
    queryset = QuestionList.activated_lists.all()
    template_name = 'question_list.html'


class AnswerQuestionListView(LoginRequiredMixin, DetailView):
    model = QuestionList
    template_name = 'question_list_details.html'

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        question_list = QuestionList.objects.get(slug=slug)

        if question_list.has_at_least_one_full_question():
            return super().get(request, *args, **kwargs)

        messages.add_message(
            request,
            messages.WARNING,
            ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE,
        )
        return redirect('questions_list')

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


class AddQuestionView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, *args, **kwargs):
        slug = self.kwargs['list_slug']
        question_list = QuestionList.objects.get(slug=slug)

        question_form = CreateQuestionForm(question_list=question_list)
        complete_list_form = CompleteListForm(question_list=question_list)
        alternatives_form = AddAlternativesForm()

        return render(
            request,
            'create_question.html',
            {
                'question_form': question_form,
                'complete_list_form': complete_list_form,
                'alternatives_form': alternatives_form,
            },
        )

    def post(self, request, *args, **kwargs):
        slug = self.kwargs['list_slug']
        question_list = QuestionList.objects.get(slug=slug)

        complete_list_form = CompleteListForm(question_list=question_list)
        if 'title' not in request.POST:
            if complete_list_form.is_valid():
                complete_list_form.save()
                return redirect('questions_list')

            messages.add_message(
                request,
                messages.ERROR,
                complete_list_form.custom_error_message,
            )

        question_form = CreateQuestionForm(
            request.POST, question_list=question_list
        )
        alternatives_form = AddAlternativesForm(request.POST)
        if question_form.is_valid() and alternatives_form.is_valid():
            question = question_form.save(commit=False)
            question.save()
            alternatives_form.save(question=question)
            return redirect('create_question', question_list.slug)

        return render(
            request,
            'create_question.html',
            {
                'question_form': question_form,
                'complete_list_form': complete_list_form,
                'alternatives_form': alternatives_form,
            },
        )

    def test_func(self):
        slug = self.kwargs['list_slug']
        question_list = QuestionList.objects.get(slug=slug)
        if (
            self.request.user == question_list.owner
            and question_list.active is False
        ):
            return True
        return False


class EditListView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = QuestionList
    template_name = 'edit_question_list.html'
    form_class = EditListForm

    def get_success_url(self):
        return reverse('lists', kwargs={'username': self.request.user})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question_list = self.get_object()
        complete_list_form = CompleteListForm(question_list=question_list)
        context['complete_list_form'] = complete_list_form

        return context

    def post(self, request, *args, **kwargs):
        question_list = self.get_object()

        if 'title' not in request.POST:
            complete_list_form = CompleteListForm(question_list=question_list)
            if not complete_list_form.is_valid():
                messages.add_message(
                    request,
                    messages.ERROR,
                    complete_list_form.custom_error_message,
                )
                return redirect('edit_list', question_list.slug)
            complete_list_form.save()
            return redirect(self.get_success_url())

        return super().post(request, *args, **kwargs)

    def test_func(self):
        slug = self.kwargs['slug']
        question_list = QuestionList.objects.get(slug=slug)
        if (
            self.request.user == question_list.owner
            and question_list.active is False
        ):
            return True
        return False


class EditQuestionView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Question
    fields = ['title']
    template_name = 'edit_question.html'
    pk_url_kwarg = 'question_id'

    def test_func(self):
        slug = self.kwargs['list_slug']
        question_list = QuestionList.objects.get(slug=slug)
        if (
            self.request.user == question_list.owner
            and question_list.active is False
        ):
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alternative_1, alternative_2 = self.object.alternatives.all()
        context['alternatives_form'] = AddAlternativesForm(
            initial={
                'alternative_1': alternative_1, 'alternative_2': alternative_2
            }
        )
        return context

    def get_success_url(self):
        list_slug = self.kwargs.get('list_slug')
        return reverse('edit_list', kwargs={'slug': list_slug})

    def post(self, request, *args, **kwargs):
        alternatives_form = AddAlternativesForm(request.POST)
        question = self.get_object()
        if alternatives_form.is_valid():
            alternatives_form.save(question=question)
        return super().post(request, *args, **kwargs)


class DeleteListView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = QuestionList
    template_name = 'delete_list.html'

    def test_func(self):
        slug = self.kwargs['slug']
        question_list = QuestionList.objects.get(slug=slug)
        if (
            self.request.user == question_list.owner
            and question_list.active is False
        ):
            return True
        return False
