# Generated by Django 5.0.6 on 2024-05-21 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0045_professor_horarios'),
    ]

    operations = [
        migrations.AddField(
            model_name='aula',
            name='tipo_status',
            field=models.CharField(choices=[('Em_andamento', 'Em_andamento'), ('Finalizada', 'Finalizada'), ('Pendente', 'Pendente')], default=1, max_length=255),
            preserve_default=False,
        ),
    ]