from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView, View

from allauth.account.decorators import verified_email_required


from questions.models import QuestionList


@method_decorator(verified_email_required, name='dispatch')
class UserListsView(LoginRequiredMixin, ListView):
    model = QuestionList
    template_name = 'user_lists.html'

    def get_queryset(self):
        username = self.kwargs['username']
        user_id = get_user_model().objects.get(username=username).id

        return super().get_queryset().filter(owner=user_id)


@method_decorator(verified_email_required, name='dispatch')
class UserStatsView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'user_stats.html'

    def get(self, request, *args, **kwargs):
        lists_created = request.user.get_amount_of_lists_created()
        return render(
            request, self.template_name, {'lists_created': lists_created}
        )

    def test_func(self):
        username = self.kwargs['username']
        if username == self.request.user.username:
            return True
        return False
