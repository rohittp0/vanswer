from django.contrib import admin

from home.models import MetaData, UrlData, FileData, Organization, OrgImages


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


class OrgImagesInline(admin.TabularInline):
    model = OrgImages
    extra = 1


@admin.register(MetaData)
class MetaDataAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status')
    search_fields = ('title', 'description')
    readonly_fields = ('status', 'verified_by', 'verified')
    list_per_page = 50

    inlines = [FileDataInline, UrlDataInline]
    actions = ["mark_as_approved", "mark_as_rejected"]

    def get_actions(self, request):
        if not request.user.is_superuser:
            return []

        return super().get_actions(request)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)

        return super().get_queryset(request).filter(contributor=request.user)

    @admin.action(description="Approve")
    def mark_as_approved(self, request, queryset):
        for meta in queryset:
            meta.verify(request.user)

    @admin.action(description="Reject")
    def mark_as_rejected(self, request, queryset):
        for meta in queryset:
            meta.verify(request.user, False)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [OrgImagesInline]
    list_per_page = 25


@admin.register(FileData)
class FileDataAdmin(admin.ModelAdmin):
    list_display = ('meta_data', 'file', 'type')
    search_fields = ('meta_data__title', 'meta_data__description', 'meta_data__keywords')
    readonly_fields = ('type', 'meta_data', 'file')
