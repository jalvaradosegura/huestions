from django.contrib.auth import get_user_model
from django.views.generic import ListView

from questions.models import QuestionList


class UserListsView(ListView):
    model = QuestionList
    template_name = 'user_lists.html'

    def get_queryset(self):
        username = self.kwargs['username']
        user_id = get_user_model().objects.get(username=username).id

        return super().get_queryset().filter(owner=user_id)
