from django.contrib import admin

from home.models import MetaData


# Register your models here.
@admin.register(MetaData)
class MetaDataAdmin(admin.ModelAdmin):
    pass
