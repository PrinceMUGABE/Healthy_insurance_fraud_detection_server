# Generated by Django 5.0.3 on 2024-04-29 21:41

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insuranceApp', '0001_initial'),
        ('patientApp', '0002_patient_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_code', models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator(message='Enter a valid patient code. This value may contain only letters, numbers, and ./- characters.', regex='^[\\w.-]+$')])),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=15, unique=True, validators=[django.core.validators.RegexValidator(message='Enter a valid phone number.', regex='^\\+?1?\\d{9,15}$')])),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('marital_status', models.CharField(choices=[('S', 'Single'), ('M', 'Married'), ('D', 'Divorced'), ('W', 'Widowed')], max_length=1)),
                ('address', models.CharField(max_length=100)),
                ('picture', models.ImageField(blank=True, null=True, upload_to='patient_pictures/')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('insurance', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='insuranceApp.insurance')),
            ],
        ),
        migrations.DeleteModel(
            name='Patient',
        ),
    ]
