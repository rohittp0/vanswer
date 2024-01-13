# Generated by Django 4.2.7 on 2024-01-08 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_metadata_organization'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='preview_image',
            field=models.ImageField(blank=True, null=True, upload_to='previews/'),
        ),
        migrations.AddField(
            model_name='organization',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='organization_img'),
        ),
    ]
