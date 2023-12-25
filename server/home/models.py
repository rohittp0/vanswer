import json
import logging

import requests
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from home.constants import language_choices, category_choices, file_types, state_choices, url_types
from vanswer.utils import ChoiceArrayField

logger = logging.getLogger("home.models")


class MetaData(models.Model):
    title = models.CharField(max_length=256, default="")
    language = models.CharField(max_length=3, choices=language_choices, default="otr")
    category = models.CharField(max_length=20, choices=category_choices, default="other")
    tags = ArrayField(models.CharField(max_length=64), size=50)
    states = ChoiceArrayField(models.CharField(max_length=10, choices=state_choices), size=32)
    description = models.TextField()
    organization = models.CharField(max_length=256, default="")
    meta_id = models.BigIntegerField(default=0, editable=False)

    description_vector = SearchVectorField(null=True, editable=False)

    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=15, default="pending")

    class Meta:
        indexes = (GinIndex(fields=["description_vector"]),)
        verbose_name = 'Record'
        verbose_name_plural = 'Records'

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super().save(force_insert, force_update, using, update_fields)

        if update_fields is None or "description" in update_fields:
            MetaData.objects.filter(pk=self.pk).update(description_vector=SearchVector("description"))

    def verify(self, user, status=True):
        if self.status == "processing" and status:
            return

        self.verified = status
        self.verified_by = user
        self.status = "approved" if status else "rejected"
        self.save()

    def __str__(self):
        return self.title


class FileData(models.Model):
    file = models.FileField(upload_to="")
    type = models.CharField(max_length=10, choices=file_types)
    meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE, related_name="file_data")

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    def __str__(self):
        return f"{self.meta_data.title}"


class UrlData(models.Model):
    url = models.URLField()
    type = models.CharField(max_length=10, choices=url_types)
    meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE, related_name="url_data")

    class Meta:
        verbose_name = 'Url'
        verbose_name_plural = 'Urls'

    def __str__(self):
        return f"{self.meta_data.title}"


@receiver(post_save, sender=MetaData)
def update_file_data(sender, instance: MetaData, created, **__):
    if created:
        return

    if instance.status != "approved":
        return

    instance.status = "processing"
    instance.save()

    url = f"{settings.VECTOR_API_URL}/upload/"

    # Serialize the MetaData object to JSON
    meta_json = {
        "name": instance.title,
        "language": instance.language,
        "type": instance.category,
        "tags": instance.tags,
        "states": instance.states,
        "description": instance.description,
        "organization": instance.organization
    }

    # Open the file in binary mode
    with open(instance.file_data.first().file.path, 'rb') as f:
        files = {
            'file': (instance.file_data.first().file.name, f, 'application/octet-stream'),
            'meta': (None, json.dumps(meta_json), 'application/json'),
        }
        try:
            response = requests.post(url, files=files)
        except requests.exceptions.ConnectionError:
            logger.error(f"Vector API connection error")
            instance.status = "failed"
            return instance.save()

    if response.status_code != 200:
        logger.error(f"Vector API error status code {response.status_code} - {response.text}")
        instance.status = "failed"
        return instance.save()

    # Get the response as JSON
    response_json = response.json()

    if response_json["status"] == "success":
        instance.meta_id = response_json["key"]
        instance.status = "processed"
    else:
        logger.error(f"Error processing file: {response_json['error']}")
        instance.status = "failed"

    instance.save()
