from django.contrib import admin

from .models import DemoList, DemoQuestion, DemoAlternative


@admin.register(DemoList)
class DemoListAdmin(admin.ModelAdmin):
    list_display = ('title', )


@admin.register(DemoAlternative)
class DemoAlternativeAdmin(admin.ModelAdmin):
    list_display = ('title', 'question')


@admin.register(DemoQuestion)
class DemoQuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'child_of')
