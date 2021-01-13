from django.contrib import admin

from .models import Alternative, Question

admin.site.register(Question)
admin.site.register(Alternative)
