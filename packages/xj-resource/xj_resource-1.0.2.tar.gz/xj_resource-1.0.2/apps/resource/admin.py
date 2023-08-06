from django.contrib import admin
from .models import ResourceImage, ResourceImageMap
# Register your models here.


class ResourceImageAdmin(admin.ModelAdmin):
    fields = ('user_id', 'title', 'url', 'filename', 'format', 'md5', ' thumb', 'snapshot')
    list_display = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'thumb', 'snapshot')
    search_fields = ('id', 'user_id', 'title', 'url', 'filename', 'format', 'md5', 'thumb', 'snapshot')


class ResourceImageMapAdmin(admin.ModelAdmin):
    fields = ('id', 'image_id', 'source_id', 'source_table', 'price',)
    list_display = ('id', 'image_id', 'source_id', 'source_table', 'price',)
    search_fields = ('id', 'image_id', 'source_id', 'source_table', 'price',)


admin.site.register(ResourceImage, ResourceImageAdmin)
admin.site.register(ResourceImageMap, ResourceImageMapAdmin)