from django.contrib import admin

from vector.models import Embedding


# Register your models here.
@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = ('meta_data', 'text')
    list_filter = ('resource_type', 'meta_data__category', 'meta_data__language')
    search_fields = ('meta_data__title', 'meta_data__description')
    ordering = ('meta_data__title',)
    readonly_fields = ('embedding', 'index', 'offset', 'meta_data', 'resource_type')
    list_per_page = 30

    def has_add_permission(self, request):
        return False
