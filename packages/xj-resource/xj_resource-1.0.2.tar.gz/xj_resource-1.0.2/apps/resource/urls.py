#_*_coding:utf-8_*_
from django.urls import re_path
from django.conf.urls import static, url
from django.conf import settings


from apps.resource.apis import resource_upload_image


urlpatterns = [
    re_path(r'^_upload_image/?$', resource_upload_image.UploadImage.as_view(), ),

    # 这里要填写/static/和/media/路径，否则django不会返回静态文件。
    re_path(
        "static/(?P<path>.*)$",
        static.serve,
        {"document_root": settings.STATIC_ROOT, "show_indexes": False},
        "static"
    ),
    re_path(
        "media/(?P<path>.*)$",
        static.serve,
        {"document_root": settings.MEDIA_ROOT, "show_indexes": False},
        "media"
    ),
]
