# Generated by Django 3.1 on 2021-03-08 02:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lists', '0002_questionlist_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionlist',
            name='description',
            field=models.TextField(blank=True, max_length=200),
        ),
    ]
