# Generated by Django 4.2.13 on 2024-07-25 02:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurancePredictionApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prediction',
            name='gender',
            field=models.CharField(max_length=6),
        ),
        migrations.AlterField(
            model_name='prediction',
            name='marital_status',
            field=models.CharField(max_length=15),
        ),
    ]
