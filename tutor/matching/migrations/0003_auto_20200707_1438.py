# Generated by Django 3.0.8 on 2020-07-07 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matching', '0002_auto_20200707_0506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='nickname',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]