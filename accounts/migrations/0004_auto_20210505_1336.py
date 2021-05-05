# Generated by Django 3.2 on 2021-05-05 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20210505_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='patient',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='therapist',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, max_length=255, null=True),
        ),
    ]