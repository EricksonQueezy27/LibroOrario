# Generated by Django 5.0.4 on 2024-04-29 11:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_story'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='story',
            old_name='conteudo',
            new_name='descricao',
        ),
        migrations.RemoveField(
            model_name='story',
            name='usuario',
        ),
        migrations.AlterField(
            model_name='story',
            name='autor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='story',
            name='imagem',
            field=models.ImageField(default=1, upload_to='images/stories/'),
            preserve_default=False,
        ),
    ]
