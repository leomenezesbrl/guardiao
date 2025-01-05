# Generated by Django 5.0.3 on 2025-01-03 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guardiao', '0009_operador_funcao_operador_nivel_acesso'),
    ]

    operations = [
        migrations.RenameField(
            model_name='material',
            old_name='quantidade',
            new_name='quantidade_disponivel',
        ),
        migrations.AddField(
            model_name='material',
            name='quantidade_emprestada',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='material',
            name='quantidade_total',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
