# Generated by Django 3.1 on 2021-04-23 23:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0003_demoalternative_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='demoalternative',
            name='votes',
            field=models.IntegerField(default=0),
        ),
    ]
