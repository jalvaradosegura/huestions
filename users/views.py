from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView, View

from core.constants import AMOUNT_OF_LISTS_PER_PAGE
from core.mixins import CustomUserPassesTestMixin
from questions.models import QuestionList
from votes.models import Vote


class UserListsView(LoginRequiredMixin, CustomUserPassesTestMixin, ListView):
    template_name = 'user_lists.html'
    paginate_by = AMOUNT_OF_LISTS_PER_PAGE

    def get_queryset(self):
        username = self.kwargs['username']
        user_id = get_user_model().objects.get(username=username).id

        filter_by = self.request.GET.get('filter')
        if filter_by == 'published':
            return (
                QuestionList.objects.filter(Q(owner=user_id) & Q(active=True))
                .prefetch_related('tags')
                .order_by('-id')
            )
        elif filter_by == 'unpublished':
            return (
                QuestionList.objects.filter(Q(owner=user_id) & Q(active=False))
                .prefetch_related('tags')
                .order_by('-id')
            )
        else:
            return (
                QuestionList.objects.filter(owner=user_id)
                .prefetch_related('tags')
                .order_by('-id')
            )


class UserStatsView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'user_stats.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        lists_created = user.get_amount_of_lists_created()
        lists_published = user.lists.filter(active=True).count()
        questions_answered = user.get_amount_of_questions_answered()

        context = {
            'lists_created': lists_created,
            'questions_answered': questions_answered,
            'lists_published': lists_published,
        }

        return render(request, self.template_name, context)

    def test_func(self):
        username = self.kwargs['username']
        if username == self.request.user.username:
            return True
        return False


class UserPlayedListsView(
    LoginRequiredMixin, CustomUserPassesTestMixin, ListView
):
    template_name = 'user_played_lists.html'
    paginate_by = AMOUNT_OF_LISTS_PER_PAGE

    def get_queryset(self):
        username = self.kwargs['username']
        user_id = get_user_model().objects.get(username=username).id
        return (
            Vote.objects.filter(user=user_id)
            .filter(~Q(list=None))
            .select_related('list')
            .prefetch_related('list__tags')
            .order_by('-list__id')
            .distinct()
        )
