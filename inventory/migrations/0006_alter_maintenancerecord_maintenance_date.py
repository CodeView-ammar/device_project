# Generated by Django 5.2 on 2025-05-10 10:35

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_checkpoint_is_checked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenancerecord',
            name='maintenance_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
