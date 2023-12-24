from django.contrib import admin

from home.models import MetaData


# Register your models here.
@admin.register(MetaData)
class MetaDataAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'organization')
    search_fields = ('title', 'description', 'keywords')
    readonly_fields = ('status', 'verified_by', 'verified')
    list_per_page = 25
