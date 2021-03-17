from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, DeleteView, UpdateView, View

from allauth.account.decorators import verified_email_required

from core.constants import (
    ALREADY_ANSWERED_ALL_THE_QUESTIONS,
    ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE,
    LIST_PUBLISHED_SUCCESSFULLY,
    QUESTION_CREATED_SUCCESSFULLY,
    QUESTION_DELETED_SUCCESSFULLY,
    QUESTION_EDITED_SUCCESSFULLY,
)
from core.mixins import CustomUserPassesTestMixin
from lists.forms import CompleteListForm
from lists.models import QuestionList
from votes.models import Vote

from .forms import AddAlternativesForm, AnswerQuestionForm, CreateQuestionForm
from .models import Alternative, Question


@login_required
@verified_email_required
def home(request):
    return render(request, 'home.html')


@method_decorator(verified_email_required, name='dispatch')
class AnswerQuestionView(LoginRequiredMixin, DetailView):
    model = QuestionList
    template_name = 'answer_question.html'

    def get(self, request, *args, **kwargs):
        slug = kwargs.get('slug')
        self.question_list = QuestionList.objects.get(slug=slug)

        if self.question_list.active:
            if (
                self.question_list.get_amount_of_unanswered_questions(
                    request.user
                )
                > 0
            ):
                return super().get(request, *args, **kwargs)
            messages.add_message(
                request, messages.INFO, ALREADY_ANSWERED_ALL_THE_QUESTIONS
            )
            return redirect('list_results', slug)

        messages.add_message(
            request,
            messages.WARNING,
            ATTEMPT_TO_SEE_AN_INCOMPLETE_LIST_MESSAGE,
        )
        return redirect('questions_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        questions_list = self.question_list.get_unanswered_questions(
            self.request.user
        )
        question = questions_list[0]
        question_id = question.id
        context['form'] = AnswerQuestionForm(question_id)
        context['question'] = question

        total_of_questions = self.question_list.questions.count()
        answered_questions_plus_one = (
            total_of_questions - len(questions_list) + 1
        )
        context['percentage'] = (
            answered_questions_plus_one / total_of_questions * 100
        )
        return context

    def post(self, request, *args, **kwargs):
        selected_alternative = Alternative.objects.get(
            id=request.POST['alternatives']
        )
        question_list = QuestionList.objects.get(
            slug=request.POST['list_slug']
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

        if question_list.get_amount_of_unanswered_questions(request.user) == 0:
            return redirect('list_results', slug=question_list.slug)

        return redirect(
            reverse(
                'answer_list',
                kwargs={'slug': question_list.slug},
            )
        )


@method_decorator(verified_email_required, name='dispatch')
class AddQuestionView(LoginRequiredMixin, CustomUserPassesTestMixin, View):
    template_name = 'create_question.html'

    def get(self, request, *args, **kwargs):
        slug = self.kwargs['list_slug']
        question_list = QuestionList.objects.get(slug=slug)

        question_form = CreateQuestionForm(question_list=question_list)
        complete_list_form = CompleteListForm(question_list=question_list)
        alternatives_form = AddAlternativesForm()

        return render(
            request,
            self.template_name,
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

        question_form = CreateQuestionForm(
            request.POST, question_list=question_list
        )
        alternatives_form = AddAlternativesForm(request.POST)

        if question_form.is_valid() and alternatives_form.is_valid():
            question = question_form.save(commit=False)
            question.save()
            alternatives_form.save(question=question)
            messages.add_message(
                request, messages.SUCCESS, QUESTION_CREATED_SUCCESSFULLY
            )

            if 'create_and_publish' in request.POST:
                complete_list_form = CompleteListForm(
                    question_list=question_list
                )
                if complete_list_form.is_valid():
                    complete_list_form.save()
                    messages.add_message(
                        request, messages.SUCCESS, LIST_PUBLISHED_SUCCESSFULLY
                    )

                return redirect('lists', request.user)
            elif 'create_and_add_another' in request.POST:
                return redirect('add_question', question_list.slug)
        return redirect('edit_list', question_list.slug)


@method_decorator(verified_email_required, name='dispatch')
class EditQuestionView(
    LoginRequiredMixin,
    CustomUserPassesTestMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = Question
    fields = ['title']
    template_name = 'edit_question.html'
    pk_url_kwarg = 'question_id'
    success_message = QUESTION_EDITED_SUCCESSFULLY

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


@method_decorator(verified_email_required, name='dispatch')
class DeleteQuestionView(
    LoginRequiredMixin, CustomUserPassesTestMixin, DeleteView
):
    model = Question
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse('edit_list', kwargs={'slug': self.kwargs.get('slug')})

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.add_message(
            self.request, messages.SUCCESS, QUESTION_DELETED_SUCCESSFULLY
        )
        return response
