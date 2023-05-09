# Generated by Django 4.2.1 on 2023-05-09 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='priority',
            field=models.CharField(choices=[('LOW', 'Faible'), ('MED', 'Moyenne'), ('HIGH', 'Élevée')], max_length=10),
        ),
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.CharField(choices=[('TODO', 'À faire'), ('IN_PRGRS', 'En cours'), ('CLOSED', 'Terminée')], max_length=10),
        ),
        migrations.AlterField(
            model_name='issue',
            name='tag',
            field=models.CharField(choices=[('BUG', 'Bug'), ('FEAT', 'Amélioration'), ('TASK', 'Tâche')], max_length=10),
        ),
        migrations.AlterField(
            model_name='project',
            name='type',
            field=models.CharField(choices=[('BACK', 'Back-end'), ('FRONT', 'Front-end'), ('IOS', 'Ios'), ('ANDROID', 'Android')], max_length=10),
        ),
    ]