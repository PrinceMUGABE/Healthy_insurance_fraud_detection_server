# Generated by Django 4.2.13 on 2024-07-12 00:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patientApp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='face_encodings',
        ),
    ]
