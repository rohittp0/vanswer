from django.contrib import admin

from home.models import MetaData, UrlData, FileData


# Register your models here.
class FileDataInline(admin.StackedInline):
    model = FileData
    fk_name = 'meta_data'
    extra = 0
    max_num = 1


class UrlDataInline(admin.StackedInline):
    model = UrlData
    fk_name = 'meta_data'
    extra = 0
    max_num = 0


@admin.register(MetaData)
class MetaDataAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status')
    search_fields = ('title', 'description', 'keywords')
    readonly_fields = ('status', 'verified_by', 'verified')
    list_per_page = 25

    inlines = [FileDataInline, UrlDataInline]
    actions = ["mark_as_approved", "mark_as_rejected"]

    def get_actions(self, request):
        if not request.user.is_superuser:
            return []

        return super().get_actions(request)

    @admin.action(description="Mark selected records as approved")
    def mark_as_approved(self, request, queryset):
        for meta in queryset:
            meta.verify(request.user)

    @admin.action(description="Mark selected records as rejected")
    def mark_as_rejected(self, request, queryset):
        for meta in queryset:
            meta.verify(request.user, False)
