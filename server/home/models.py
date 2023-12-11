from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models


# Create your models here.

class MetaData(models.Model):
    name = models.CharField(max_length=256, default="")
    language = models.CharField(max_length=256, default="")
    type = models.CharField(max_length=256, default="Other")
    tags = ArrayField(models.CharField(max_length=64), size=50)
    states = ArrayField(models.CharField(max_length=64), size=32)
    description = models.TextField()
    organization = models.CharField(max_length=256, default="")
    meta_id = models.BigIntegerField(default=0, editable=False)
    file = models.FileField()

    description_vector = SearchVectorField(null=True, editable=False)

    class Meta:
        indexes = (GinIndex(fields=["description_vector"]),)

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.description_vector = SearchVector('description')
        super().save(force_insert, force_update, using, update_fields)

    def __str__(self):
        return self.name
