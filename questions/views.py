from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import redirect, render, reverse
from django.views.generic import DetailView, UpdateView, View

from core.constants import ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE
from core.mixins import CustomUserPassesTestMixin
from lists.forms import CompleteListForm
from lists.models import QuestionList
from lists.views import DeleteListView
from votes.models import Vote

from .forms import AddAlternativesForm, AnswerQuestionForm, CreateQuestionForm
from .models import Alternative, Question


@login_required
def home(request):
    return render(request, 'home.html')


class AnswerListView(LoginRequiredMixin, DetailView):
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
        question_list = QuestionList.objects.get(
            id=request.POST['question_list_id']
        )
        if not selected_alternative.question.has_the_user_already_voted(
            self.request.user
        ):
            selected_alternative.vote_for_this_alternative(self.request.user)
            Vote.objects.create(
                user=self.request.user,
                list=question_list,
                question=selected_alternative.question,
                alternative=selected_alternative,
            )

        if 'next_page' in request.POST:
            next_page = request.POST['next_page']
            return redirect(
                reverse(
                    'answer_list',
                    kwargs={'slug': question_list.slug},
                )
                + f'?page={next_page}'
            )
        return redirect('list_results', slug=question_list.slug)


class AddQuestionView(LoginRequiredMixin, CustomUserPassesTestMixin, View):
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
                'question_list_slug': question_list.slug,
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
            return redirect('add_question', question_list.slug)

        return render(
            request,
            'create_question.html',
            {
                'question_form': question_form,
                'complete_list_form': complete_list_form,
                'alternatives_form': alternatives_form,
                'question_list_slug': question_list.slug,
            },
        )


class EditQuestionView(
    LoginRequiredMixin, CustomUserPassesTestMixin, UpdateView
):
    model = Question
    fields = ['title']
    template_name = 'edit_question.html'
    pk_url_kwarg = 'question_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        alternative_1, alternative_2 = self.object.alternatives.all()
        context['alternatives_form'] = AddAlternativesForm(
            initial={
                'alternative_1': alternative_1,
                'alternative_2': alternative_2,
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


class DeleteQuestionView(DeleteListView):
    model = Question
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse('edit_list', kwargs={'slug': self.kwargs.get('slug')})
