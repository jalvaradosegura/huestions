# Generated by Django 3.1 on 2021-02-14 20:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionlist',
            name='owner',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='lists',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
