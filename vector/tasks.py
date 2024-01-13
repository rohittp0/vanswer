from django.db.models.signals import post_save
from django.dispatch import receiver

from home.models import FileData, MetaData
from vector.models import Embedding
from vector.operations import process_pdf, elements_to_embeddings


def get_embeddings(file_data: FileData):
    if file_data.type != "pdf":
        return []

    pdf_elements = process_pdf(file_data.file.path)
    return elements_to_embeddings(pdf_elements)


@receiver(post_save, sender=MetaData)
def generate_embeddings(sender, instance: MetaData, created, **__):
    if created or instance.status != "approved":
        return

    if instance.file_data.count() == 0:
        instance.status = "no_files"
        instance.save()

    instance.status = "processing"
    instance.save()

    instance.embeddings.all().delete()

    for i, file_data in enumerate(instance.file_data.all()):
        embeddings = get_embeddings(file_data)

        for embedding in embeddings:
            Embedding.objects.create(
                embedding=embedding["embedding"],
                index=i,
                offset=embedding["index"],
                meta_data=instance,
                resource_type="file",
                text=embedding["text"]
            )

    instance.status = "processed"
