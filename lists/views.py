import datetime

from allauth.account.decorators import verified_email_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Q
from django.shortcuts import redirect, render, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DeleteView, DetailView, ListView, UpdateView

from core.constants import (
    AMOUNT_OF_DAYS_FOR_POPULARITY,
    AMOUNT_OF_LISTS_PER_PAGE,
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
    template_name = 'lists.html'
    paginate_by = AMOUNT_OF_LISTS_PER_PAGE

    def get_queryset(self):
        date_to_compare_against = timezone.now() - datetime.timedelta(
            days=AMOUNT_OF_DAYS_FOR_POPULARITY
        )
        return (
            (
                QuestionList.objects.filter(
                    votes__created__gte=date_to_compare_against
                )
                .annotate(votes_amount=Count('id'))
                .order_by('-votes_amount')
            )
            .select_related('owner')
            .prefetch_related('tags')
        )


@method_decorator(verified_email_required, name='dispatch')
class ListResultsView(LoginRequiredMixin, DetailView):
    template_name = 'list_results.html'

    def get_queryset(self):
        return QuestionList.objects.all().prefetch_related(
            'questions__alternatives__users'
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        list_slug = self.object.slug

        if self.object.get_amount_of_unanswered_questions(request.user) == 0:
            self.shared_by = kwargs.get('username', '')
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)

        messages.add_message(
            request, messages.INFO, MUST_COMPLETE_LIST_BEFORE_SEING_RESULTS
        )
        if 'username' in kwargs:
            return redirect('answer_list', list_slug, self.kwargs['username'])
        return redirect('answer_list', list_slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questions = self.object.questions.all()

        user_alternatives = []
        for q in questions:
            user_alternatives.append(
                [q, q.get_user_voted_alternative(self.request.user)]
            )
        context['questions_and_user_alternatives'] = user_alternatives

        if self.shared_by:
            shared_by = CustomUser.objects.get(username=self.shared_by)
            if self.object.get_amount_of_unanswered_questions(shared_by) == 0:
                shared_alternatives = []
                for q in questions:
                    shared_alternatives.append(
                        [
                            q,
                            q.get_user_voted_alternative(self.request.user),
                            q.get_user_voted_alternative(shared_by),
                        ]
                    )
                context['shared_user'] = shared_by
                context[
                    'questions_and_user_alternatives'
                ] = shared_alternatives
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
            form.save_m2m()  # django-taggit
            messages.add_message(
                request, messages.SUCCESS, LIST_CREATED_SUCCESSFULLY
            )
            return redirect('add_question', question_list.slug)
        return render(request, 'create_list.html', {'form': form})

    form = CreateQuestionListForm(owner=request.user)
    print('form:', form.__dict__)
    print('form 2:', form.fields['title'].__dict__)
    print('form 3:', form.fields['tags'].__dict__)

    return render(request, 'create_list.html', {'form': form})


@method_decorator(verified_email_required, name='dispatch')
class EditListView(
    LoginRequiredMixin,
    CustomUserPassesTestMixin,
    SuccessMessageMixin,
    UpdateView,
):
    template_name = 'edit_list.html'
    form_class = EditListForm
    success_message = LIST_EDITED_SUCCESSFULLY

    def get_queryset(self):
        return QuestionList.objects.all().prefetch_related(
            'questions__alternatives'
        )

    def get_success_url(self):
        return reverse('lists', kwargs={'username': self.request.user})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sorted_questions'] = self.object.questions.all()
        context['complete_list_form'] = CompleteListForm(
            question_list=self.object
        )

        return context

    def post(self, request, *args, **kwargs):
        question_list = self.get_object()
        self.object = question_list

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

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


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


@method_decorator(verified_email_required, name='dispatch')
class SearchListsView(LoginRequiredMixin, ListView):
    context_object_name = 'lists'
    template_name = 'search_results.html'
    paginate_by = AMOUNT_OF_LISTS_PER_PAGE

    def get_queryset(self):
        self.q = self.request.GET.get('q')
        return (
            QuestionList.activated_lists.filter(
                Q(title__icontains=self.q) | Q(tags__name__icontains=self.q)
            )
            .order_by('-id')
            .prefetch_related('tags')
            .select_related('owner')
        )

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.q
        return context
