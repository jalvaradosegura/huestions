# Generated by Django 3.1 on 2021-03-03 12:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0002_auto_20210303_1204'),
        ('lists', '0001_initial'),
        ('questions', '0003_questionlist_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='child_of',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='lists.questionlist'),
        ),
        migrations.DeleteModel(
            name='QuestionList',
        ),
    ]
