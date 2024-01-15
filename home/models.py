import os
from pathlib import Path

import fitz
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models

from home.constants import language_choices, category_choices, file_types, state_choices, url_types, status_choices
from vanswer.utils import ChoiceArrayField


class Organization(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    website = models.URLField()
    logo = models.ImageField(upload_to="organization_logo", null=True, blank=True)

    def __str__(self):
        return self.name


class OrgImages(models.Model):
    org = models.ForeignKey(Organization, default=None, on_delete=models.CASCADE, related_name="org_images")
    image = models.ImageField(upload_to="organization_img", verbose_name="image")

    class Meta:
        verbose_name = 'Carousel Image'
        verbose_name_plural = 'Carousel Images'


class MetaData(models.Model):
    title = models.CharField(max_length=256, default="")
    language = models.CharField(max_length=3, choices=language_choices, default="otr")
    category = models.CharField(max_length=20, choices=category_choices, default="other")
    tags = ArrayField(models.CharField(max_length=64), size=50)
    states = ChoiceArrayField(models.CharField(max_length=10, choices=state_choices), size=32)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="records")
    meta_id = models.BigIntegerField(default=0, editable=False)
    date = models.DateField(default="2000-01-01")
    contributor = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, related_name="contributions")

    description_vector = SearchVectorField(null=True, editable=False)

    verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name="verifications")
    status = models.CharField(max_length=10, choices=status_choices, default="processing")

    preview_image = models.ImageField(upload_to='previews/', blank=True, null=True)

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

        if status and self.file_data.count() > 0:
            from vector.tasks import generate_embeddings_task
            generate_embeddings_task.delay(self.id)

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.type == 'pdf' and not self.meta_data.preview_image:
            self.create_preview_image()

    def create_preview_image(self):
        pdf_path = self.file.path

        # Directory to save the preview image
        output_folder = os.path.join(settings.MEDIA_ROOT, 'previews')
        os.makedirs(output_folder, exist_ok=True)

        doc = fitz.open(pdf_path)

        if len(doc) > 0:  # Check if there's at least one page
            page = doc.load_page(0)  # First page

            # Render the page to a pixmap (an image)
            pix = page.get_pixmap(dpi=72)  # or use another DPI value as needed

            # Create the preview image path
            preview_image_name = f'preview_{self.pk}.png'  # PNG is better for quality
            image_path = Path(output_folder) / preview_image_name

            # Save the pixmap as an image
            pix.save(str(image_path))

            # Set the relative path of the preview image in the model
            image_relative_path = image_path.relative_to(Path(settings.MEDIA_ROOT))
            self.meta_data.preview_image = str(image_relative_path)
            self.meta_data.save()


class UrlData(models.Model):
    url = models.URLField()
    type = models.CharField(max_length=10, choices=url_types)
    meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE, related_name="url_data")

    class Meta:
        verbose_name = 'Url'
        verbose_name_plural = 'Urls'

    def __str__(self):
        return f"{self.meta_data.title}"
