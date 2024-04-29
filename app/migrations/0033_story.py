# Generated by Django 5.0.4 on 2024-04-29 10:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0032_remove_disciplina_turma_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('autor', models.CharField(choices=[('Professor', 'Professor'), ('Encarregado', 'Encarregado'), ('Gestor', 'Gestor')], max_length=50)),
                ('titulo', models.CharField(max_length=100)),
                ('conteudo', models.TextField()),
                ('data_publicacao', models.DateTimeField(auto_now_add=True)),
                ('imagem', models.ImageField(blank=True, null=True, upload_to='story_images/')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]