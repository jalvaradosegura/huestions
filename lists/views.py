from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from allauth.account.decorators import verified_email_required

from core.constants import (
    LIST_CREATED_SUCCESSFULLY,
    LIST_DELETED_SUCCESSFULLY,
    LIST_EDITED_SUCCESSFULLY,
    LIST_PUBLISHED_SUCCESSFULLY,
    MUST_COMPLETE_LIST_BEFORE_SEING_RESULTS,
    USER_THAT_SHARED_LIST_HAVENT_COMPLETED_IT,
)
from core.mixins import CustomUserPassesTestMixin
from users.models import CustomUser

from .forms import CompleteListForm, CreateQuestionListForm, EditListForm
from .models import QuestionList


@method_decorator(verified_email_required, name='dispatch')
class QuestionsListView(LoginRequiredMixin, ListView):
    queryset = QuestionList.activated_lists.all()
    template_name = 'lists.html'


@method_decorator(verified_email_required, name='dispatch')
class ListResultsView(LoginRequiredMixin, DetailView):
    model = QuestionList
    template_name = 'list_results.html'

    def get(self, request, *args, **kwargs):
        list_slug = kwargs.get('slug')
        question_list = QuestionList.objects.get(slug=list_slug)

        if question_list.get_amount_of_unanswered_questions(request.user) == 0:
            self.shared_by = kwargs.get('username', '')
            return super().get(request, *args, **kwargs)

        messages.add_message(
            request, messages.INFO, MUST_COMPLETE_LIST_BEFORE_SEING_RESULTS
        )
        if 'username' in kwargs:
            return redirect('answer_list', list_slug, self.kwargs['username'])
        return redirect('answer_list', list_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = self.object.questions.all()
        user_alternatives = [
            q.get_user_voted_alternative(self.request.user) for q in questions
        ]
        context['questions_and_user_alternatives'] = list(
            zip(questions, user_alternatives)
        )

        if self.shared_by:
            shared_by = CustomUser.objects.get(username=self.shared_by)
            if self.object.get_amount_of_unanswered_questions(shared_by) == 0:
                shared_alternatives = [
                    q.get_user_voted_alternative(shared_by) for q in questions
                ]
                context['shared_user'] = shared_by
                context['questions_and_user_alternatives'] = list(
                    zip(questions, user_alternatives, shared_alternatives)
                )
            else:
                messages.add_message(
                    self.request,
                    messages.INFO,
                    USER_THAT_SHARED_LIST_HAVENT_COMPLETED_IT,
                )

        return context


@login_required
@verified_email_required
def create_list(request):
    if request.method == 'POST':
        form = CreateQuestionListForm(request.POST, owner=request.user)

        if form.is_valid():
            question_list = form.save(commit=False)
            question_list.save()
            messages.add_message(
                request, messages.SUCCESS, LIST_CREATED_SUCCESSFULLY
            )
            return redirect('add_question', question_list.slug)
        return render(request, 'create_list.html', {'form': form})

    form = CreateQuestionListForm(owner=request.user)
    return render(request, 'create_list.html', {'form': form})


@method_decorator(verified_email_required, name='dispatch')
class EditListView(
    LoginRequiredMixin,
    CustomUserPassesTestMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = QuestionList
    template_name = 'edit_list.html'
    form_class = EditListForm
    success_message = LIST_EDITED_SUCCESSFULLY

    def get_success_url(self):
        return reverse('lists', kwargs={'username': self.request.user})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sorted_questions'] = self.object.questions.order_by('id')
        context['complete_list_form'] = CompleteListForm(
            question_list=self.object
        )

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
            messages.add_message(
                request, messages.SUCCESS, LIST_PUBLISHED_SUCCESSFULLY
            )
            return redirect(self.get_success_url())

        return super().post(request, *args, **kwargs)


@method_decorator(verified_email_required, name='dispatch')
class DeleteListView(
    LoginRequiredMixin, CustomUserPassesTestMixin, DeleteView
):
    model = QuestionList
    template_name = 'delete_list.html'

    def get_success_url(self):
        return reverse('lists', kwargs={'username': self.request.user})

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.add_message(
            self.request, messages.SUCCESS, LIST_DELETED_SUCCESSFULLY
        )
        return response
