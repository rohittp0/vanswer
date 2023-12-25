from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models

from home.constants import language_choices, category_choices, file_types, state_choices, url_types


class MetaData(models.Model):
    title = models.CharField(max_length=256, default="")
    language = models.CharField(max_length=3, choices=language_choices, default="other")
    category = models.CharField(max_length=20, choices=category_choices, default="other")
    tags = ArrayField(models.CharField(max_length=64), size=50)
    states = ArrayField(models.CharField(max_length=10, choices=state_choices), size=32)
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

    def verify(self, user):
        self.verified = True
        self.verified_by = user
        self.status = "processing"
        self.save()

    def __str__(self):
        return self.title


class FileData(models.Model):
    file = models.ForeignKey(MetaData, on_delete=models.CASCADE)
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
