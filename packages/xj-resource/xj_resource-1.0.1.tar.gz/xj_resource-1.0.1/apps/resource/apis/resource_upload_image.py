import os
import re
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

# from apps.user.services import UserService
from main.settings import STATICFILES_DIRS
from main.settings import STATIC_URL
from ..utils.digit_algorithm import DigitAlgorithm
from ..utils.file_operate import FileOperate
from ..models import *


# 声明序列化
class UploadImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceImage
        # 序列化验证检查，检查必填项的字段
        fields = ['id', 'user_id', 'title', 'url', 'filename', 'format', 'md5']


class UploadImage(APIView):
    params = None
    serializer_params = None

    print("-" * 30, os.path.basename(__file__), "-" * 30)

    # POST方法，上传图片
    def post(self, request, *args, **kwargs):
        # param = self.params = request.query_params  # 返回QueryDict类型
        param = self.params = request.data  # 返回QueryDict类型
        item = self.serializer_params = {}  # 将要写入的某条数据
        print(">>> param", param)

        # ========== 一、检查：验证权限 ==========
        token = self.request.META.get('HTTP_AUTHORIZATION', '')
        if not token:
            return Response({'err': 6001, 'msg': '缺少Token', })
        user_id = UserService.checkToken(token)
        item['user_id'] = user_id
        if not user_id:
            return Response({'err': 6002, 'msg': 'token验证失败', })

        # ========== 二、检查：必填性 ==========
        # 对应postman的Body的key=file，value=上传文件的名称 watermelonhh.jpg
        input_file = request.FILES.get("image")
        if input_file is None:
            return Response({'err': 2001, 'msg': '未选择上传图片', })

        # ========== 三、检查：内容的准确性 ==========
        ret = re.search(r'(.*)\.(\w{3,4})$', input_file.name)
        if not ret:
            return Response({'err': 3001, 'msg': '上传的文件名不合法', })
        input_filename = item['filename'] = ret.group(1)
        format = item['format'] = ret.group(2)

        if format not in ('jpg', 'jpeg', 'gif', 'png', 'svg'):
            return Response({'err': 3002, 'msg': '上传的文件类型错误，应为jpg、jpeg、gif、png、svg', })

        title = item['title'] = param.get('title', input_filename)

        # ========== 四、获取并处理参数 ===========
        filename = item['filename'] = 'img_' + DigitAlgorithm.make_datetime_17() + '.' + format
        # 上传文件本地保存路径， image是static文件夹下专门存放图片的文件夹
        url = item['url'] = 'upload/images/' + filename
        # print(">>>", request.headers['Host'])

        folder_name = os.path.join(STATICFILES_DIRS[0], 'upload/images/')
        # 没有该目录，则创建
        FileOperate.make_dir(folder_name=folder_name)

        local_path = os.path.join(STATICFILES_DIRS[0], 'upload/images/' + filename)

        with open(local_path, 'wb') as f:
            f.write(input_file.read())
            # print("文件上传完毕")

        item['snapshot'] = {
            'origin_filename': input_filename + '.' + format
        }

        print(">>> make_file_md5:", DigitAlgorithm.make_file_md5(file=local_path))
        item['md5'] = DigitAlgorithm.make_file_md5(file=local_path)
        if not item['md5']:
            return Response({'err': 3003, 'msg': 'local_path不存在', })

        # ========== 五、数据处理 ==========
        serializer = UploadImageSerializer(data=item, context={})
        # 序列化验证，验证失败则获取错误信息
        if not serializer.is_valid():
            print(">>> serializer.errors:", serializer.errors, "\n")
            return Response({'err': 5001, 'msg': serializer.errors, })

        print(">>> item: ", item)

        # 验证成功，保存数据进数据库
        image_instance = serializer.save()

        data_list = {
            'id': image_instance.id,
            'title': title,
            'url': 'http://' + request.headers['Host'] + STATIC_URL + url,
            'path': STATIC_URL + url,
            'filename': filename,
            'format': format,
            'md5': item['md5'],
            # 'thumb': item['thumb'],
            # 'snapshot': snapshot,
        }

        return Response({
            'err': 0,
            'msg': 'OK',
            'data': data_list,
        })







