from django.contrib import admin

from .models import Question, Alternative

admin.site.register(Question)
admin.site.register(Alternative)
