# encoding: utf-8
"""
@project: djangoModel->resource_upload_file
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 文件上传接口
@created_time: 2022/8/2 10:28
"""
from django.core.paginator import Paginator
from rest_framework.views import APIView

from xj_resource.models import ResourceFile
from xj_resource.services.upload_file_service import UploadFileService
from xj_resource.utils.custom_response import util_response
from xj_resource.utils.model_handle import only_filed_handle, parse_model


class UploadFile(APIView):
    def post(self, request):
        user_id = request.user.id or 0
        file = request.FILES.get('file')
        title = request.POST.get('title', '')
        group_id = request.POST.get('group_id', 0)

        uploader = UploadFileService(input_file=file)
        info = uploader.info_detail()
        # 获取信息，并把非素材上传信息补全
        info['title'] = title or info['snapshot']['old_filename']
        info['user_id'] = user_id
        info['group_id'] = group_id
        # 写入磁盘
        uploader.write_disk()
        # 写入数据库
        image_instance = uploader.save_to_db(info)
        if image_instance:
            info['id'] = image_instance.id
        if not uploader.is_valid():
            return util_response(err=4003, msg=uploader.get_error_message())
        return util_response(data=info)

    # 文件列表
    def get(self, request):
        params = request.query_params.copy()
        limit = params.pop('limit', 20)
        page = params.pop('page', 20)
        params = only_filed_handle(params, {
            "title": "title__contains",
            "filename": "filename_contains",
            "md5": "md5",
            "user_id": "user_id"
        }, None)
        list_obj = ResourceFile.objects.filter(**params)
        count = list_obj.count()
        res_set = Paginator(list_obj, limit).get_page(page)
        return util_response(data={'count': count, 'page': page, 'limit': limit, "list": parse_model(res_set)})
