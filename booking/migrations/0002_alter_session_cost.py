# Generated by Django 3.2 on 2021-05-03 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='cost',
            field=models.IntegerField(),
        ),
    ]
