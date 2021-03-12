from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.generic import ListView

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
