from django.contrib import admin

from .models import Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'list', 'question', 'alternative')
