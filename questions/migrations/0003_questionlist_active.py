# Generated by Django 3.1 on 2021-02-15 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0002_questionlist_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionlist',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]