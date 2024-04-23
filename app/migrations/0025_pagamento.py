# Generated by Django 5.0.3 on 2024-04-12 11:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0024_boletim'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('Folha de Prova', 'Folha de Prova'), ('Passe', 'Passe'), ('Propina', 'Propina'), ('Dívida', 'Dívida')], max_length=100)),
                ('valor', models.DecimalField(decimal_places=2, max_digits=10)),
                ('comprovativo', models.ImageField(upload_to='comprovativos_pagamento/')),
                ('data_pagamento', models.DateField(auto_now_add=True)),
                ('encarregado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.encarregado')),
            ],
        ),
    ]