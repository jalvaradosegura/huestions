from django.contrib import admin

from .models import Alternative, Question, QuestionList

admin.site.register(Alternative)
admin.site.register(Question)
admin.site.register(QuestionList)
