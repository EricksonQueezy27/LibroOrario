# Generated by Django 5.0.3 on 2024-04-09 21:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_informacoesacademicas_aluno'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comportamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.TextField()),
                ('ausencias_nao_justificadas', models.IntegerField(default=0)),
                ('comportamento', models.CharField(max_length=100)),
                ('aluno', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.aluno')),
            ],
        ),
    ]