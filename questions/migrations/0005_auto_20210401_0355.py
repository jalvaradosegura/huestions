# Generated by Django 3.1 on 2021-04-01 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0004_alternative_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alternative',
            name='image',
            field=models.ImageField(
                default='default_alternative.jpg', upload_to='alternative_pics'
            ),
        ),
    ]
