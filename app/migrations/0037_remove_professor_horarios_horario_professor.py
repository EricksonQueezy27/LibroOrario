# Generated by Django 5.0.4 on 2024-04-29 19:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0036_feedback_pesquisa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='professor',
            name='horarios',
        ),
        migrations.AddField(
            model_name='horario',
            name='professor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.professor'),
            preserve_default=False,
        ),
    ]
