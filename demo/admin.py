from django.contrib import admin

from .models import DemoAlternative, DemoList, DemoQuestion


@admin.register(DemoList)
class DemoListAdmin(admin.ModelAdmin):
    list_display = ('title',)


@admin.register(DemoAlternative)
class DemoAlternativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'question')


@admin.register(DemoQuestion)
class DemoQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'child_of')
