# encoding: utf-8
"""
@project: djangoModel->recycle_bin_add
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 删除数据并放入回收站
@created_time: 2022/6/9 13:28
"""

# 使用案例
from django.http import JsonResponse
from rest_framework.views import APIView

from ..services.recycle_service import RecycleService
from ..tool import parse_data


class RecycleBinAddExample(APIView):
    # 使用案例方法
    def post(self, request):
        params = parse_data(request.POST)
        RecycleService.put_recycle_bin(**params)
        return JsonResponse({'err': 0, 'data': params, 'msg': 'ok'})
