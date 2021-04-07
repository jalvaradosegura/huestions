from django.contrib import admin

from .models import Alternative, Question


@admin.register(Alternative)
class AlternativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'question')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'child_of')
