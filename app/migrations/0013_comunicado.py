# Generated by Django 5.0.3 on 2024-04-09 11:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_disciplinaselecionada'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comunicado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('mensagem', models.TextField()),
                ('data_publicacao', models.DateTimeField(auto_now_add=True)),
                ('requerido_pagamento', models.BooleanField(default=False)),
                ('encarregado_destino', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.encarregado')),
            ],
        ),
    ]