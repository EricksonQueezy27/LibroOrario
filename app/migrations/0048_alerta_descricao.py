# Generated by Django 5.0.6 on 2024-05-22 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0047_alerta'),
    ]

    operations = [
        migrations.AddField(
            model_name='alerta',
            name='descricao',
            field=models.TextField(default=1, max_length=5000),
            preserve_default=False,
        ),
    ]