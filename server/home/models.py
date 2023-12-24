from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models

from home.constants import language_choices, type_choices, format_choices, state_choices


class MetaData(models.Model):
    title = models.CharField(max_length=256, default="")
    language = models.CharField(max_length=3, choices=language_choices, default="other")
    type = models.CharField(max_length=20, choices=type_choices, default="other")
    format = models.CharField(max_length=10, choices=format_choices, default="other")
    tags = ArrayField(models.CharField(max_length=64), size=50)
    states = ArrayField(models.CharField(max_length=10, choices=state_choices), size=32)
    description = models.TextField()
    organization = models.CharField(max_length=256, default="")
    meta_id = models.BigIntegerField(default=0, editable=False)
    file = models.FileField()

    description_vector = SearchVectorField(null=True, editable=False)

    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=15, default="pending")

    class Meta:
        indexes = (GinIndex(fields=["description_vector"]),)
        verbose_name = 'File'
        verbose_name_plural = 'Files'

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
