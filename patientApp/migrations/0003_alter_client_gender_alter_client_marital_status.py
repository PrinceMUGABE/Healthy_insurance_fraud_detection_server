# Generated by Django 4.2.13 on 2024-07-16 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patientApp', '0002_remove_client_face_encodings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='gender',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='client',
            name='marital_status',
            field=models.CharField(max_length=15),
        ),
    ]
