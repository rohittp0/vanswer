# Generated by Django 4.2.7 on 2024-01-13 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vector', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='embedding',
            name='text',
            field=models.TextField(default=''),
        ),
        migrations.AlterField(
            model_name='embedding',
            name='resource_type',
            field=models.CharField(choices=[('file', 'file'), ('url', 'url')], max_length=5),
        ),
    ]