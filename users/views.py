from allauth.account.decorators import verified_email_required
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View

from core.constants import AMOUNT_OF_LISTS_PER_PAGE
from questions.models import QuestionList


@method_decorator(verified_email_required, name='dispatch')
class UserListsView(LoginRequiredMixin, ListView):
    model = QuestionList
    template_name = 'user_lists.html'
    paginate_by = AMOUNT_OF_LISTS_PER_PAGE
    ordering = '-id'

    def get_queryset(self):
        username = self.kwargs['username']
        user_id = get_user_model().objects.get(username=username).id

        return super().get_queryset().filter(owner=user_id)


@method_decorator(verified_email_required, name='dispatch')
class UserStatsView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'user_stats.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        lists_created = user.get_amount_of_lists_created()
        questions_answered = user.get_amount_of_questions_answered()

        context = {
            'lists_created': lists_created,
            'questions_answered': questions_answered,
        }

        return render(request, self.template_name, context)

    def test_func(self):
        username = self.kwargs['username']
        if username == self.request.user.username:
            return True
        return False
