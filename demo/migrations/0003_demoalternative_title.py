# Generated by Django 3.1 on 2021-04-23 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0002_demoalternative_demoquestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='demoalternative',
            name='title',
            field=models.CharField(default='', max_length=100, verbose_name='title'),
        ),
    ]