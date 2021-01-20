from django.contrib import admin

from .models import Alternative, Question, QuestionList


@admin.register(Alternative)
class AlternativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'question')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'child_of')


@admin.register(QuestionList)
class QuestionListAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')
    prepopulated_fields = {'slug': ('title',)}
