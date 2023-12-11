from django.contrib.postgres.fields import ArrayField
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
    meta_id = models.BigIntegerField(default=0)
