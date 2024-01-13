from django.db import models
from pgvector.django import VectorField

from home.models import MetaData


class Embedding(models.Model):
    embedding = VectorField(dimensions=384)
    index = models.IntegerField(default=-1)
    offset = models.IntegerField(default=-1)
    meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE, related_name="embeddings")
    resource_type = models.CharField(max_length=5, choices=(('file', 'file'), ('url', 'url')))

    def __str__(self):
        return self.meta_data.title
