from django.views.generic import ListView

from .models import CustomUser


class UserListsView(ListView):
    model = CustomUser
    template_name = 'user_lists.html'
