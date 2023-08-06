from django.core.paginator import Paginator
from rest_framework.views import APIView

from xj_resource.models import *
from xj_resource.services.upload_image_service import UploadImageService
from xj_resource.utils.model_handle import util_response, only_filed_handle, parse_model


class UploadImage(APIView):
    def post(self, request):
        user_id = request.user.id or 0
        file = request.FILES.get('image')
        title = request.POST.get('title', '')
        group_id = request.POST.get('group_id', 0)

        uploader = UploadImageService(input_file=file)
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
        list_obj = ResourceImage.objects.filter(**params)
        count = list_obj.count()
        res_set = Paginator(list_obj, limit).get_page(page)
        return util_response(data={'count': count, 'page': page, 'limit': limit, "list": parse_model(res_set)})
