# Generated by Django 3.2 on 2021-05-08 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20210505_1344'),
        ('booking', '0004_alter_appointment_patients'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='patients',
            field=models.ManyToManyField(related_name='appointment_participants', to='accounts.Patient'),
        ),
    ]
