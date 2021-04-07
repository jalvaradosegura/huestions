from django.contrib import admin

from .models import QuestionList


@admin.register(QuestionList)
class QuestionListAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
