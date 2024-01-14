from celery import shared_task
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from home.models import FileData, MetaData
from vector.models import Embedding
from vector.operations import process_pdf, elements_to_embeddings, texts_to_embeddings


def get_embeddings(file_data: FileData):
    if file_data.type != "pdf":
        return []

    pdf_elements = process_pdf(file_data.file.path)
    return elements_to_embeddings(pdf_elements)


@shared_task
def generate_embeddings_task(meta_id: int):
    instance = MetaData.objects.get(id=meta_id)

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
    instance.save()


@shared_task
def update_embedding_task(embedding_id: int):
    embedding = Embedding.objects.get(id=embedding_id)
    embedding.embedding = texts_to_embeddings([embedding.text])[0]
    embedding.save()


@receiver(post_save, sender=MetaData)
def generate_embeddings(sender, instance, created, **_):
    if created or instance.status != "approved":
        return

    if instance.file_data.count() == 0:
        instance.status = "no_files"
        instance.save()

    generate_embeddings_task.delay(instance.id)


@receiver(pre_save, sender=Embedding)
def update_embedding(sender, instance, **kwargs):
    # return if instance.text has not changed
    if kwargs['update_fields'] is None or "text" not in kwargs['update_fields']:
        return

    update_embedding_task.delay(instance.id)
