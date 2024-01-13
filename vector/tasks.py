from django.db.models.signals import post_save
from django.dispatch import receiver

from home.models import FileData, MetaData
from vector.models import Embedding


def get_embeddings(file_data: FileData):
    return []


@receiver(post_save, sender=MetaData)
def generate_embeddings(sender, instance: MetaData, created, **__):
    if created or instance.status != "approved":
        return

    if instance.file_data.count() == 0:
        return

    instance.status = "processing"
    instance.save()

    instance.embeddings.all().delete()

    for i, file_data in enumerate(instance.file_data.all()):
        embeddings = get_embeddings(file_data)

        for j, embedding in enumerate(embeddings):
            Embedding.objects.create(
                embedding=embedding,
                index=i,
                offset=j,
                meta_data=instance,
                resource_type=file_data.type
            )

    instance.status = "processed"
