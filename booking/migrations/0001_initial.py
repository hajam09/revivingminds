# Generated by Django 3.2 on 2021-05-03 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_name', models.CharField(max_length=255)),
                ('cost', models.DecimalField(decimal_places=2, max_digits=5)),
                ('quantity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('zoom_link', models.URLField(max_length=500)),
                ('participants', models.ManyToManyField(related_name='appointment_participants', to='accounts.Patient')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.patient')),
                ('session_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='booking.session')),
                ('therapist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.therapist')),
            ],
        ),
    ]
