# Generated by Django 4.2.7 on 2023-12-11 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='file',
            field=models.FileField(default='', upload_to='files/'),
            preserve_default=False,
        ),
    ]
