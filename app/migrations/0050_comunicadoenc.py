# Generated by Django 5.0.3 on 2024-05-23 11:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0049_alerta2'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComunicadoEnc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('mensagem', models.TextField()),
                ('data_publicacao', models.DateTimeField(auto_now_add=True)),
                ('professor_autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.professor')),
                ('turmas_destino', models.ManyToManyField(blank=True, to='app.turma')),
            ],
        ),
    ]
