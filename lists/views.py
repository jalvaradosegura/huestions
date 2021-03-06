from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render, reverse
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from core.constants import (
    LIST_CREATED_SUCCESSFULLY,
    LIST_DELETED_SUCCESSFULLY,
    LIST_EDITED_SUCCESSFULLY,
    LIST_PUBLISHED_SUCCESSFULLY,
)
from core.mixins import CustomUserPassesTestMixin

from .forms import CompleteListForm, CreateQuestionListForm, EditListForm
from .models import QuestionList


class QuestionsListView(LoginRequiredMixin, ListView):
    queryset = QuestionList.activated_lists.all()
    template_name = 'lists.html'


class ListResultsView(LoginRequiredMixin, DetailView):
    model = QuestionList
    template_name = 'list_results.html'


@login_required
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

    form = CreateQuestionListForm(owner=request.user)
    return render(request, 'create_list.html', {'form': form})


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
            messages.add_message(
                request, messages.SUCCESS, LIST_PUBLISHED_SUCCESSFULLY
            )
            return redirect(self.get_success_url())

        return super().post(request, *args, **kwargs)


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
