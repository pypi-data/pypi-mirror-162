# _*_coding:utf-8_*_

import logging

from django.core.paginator import Paginator
from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import RecycleBin

logger = logging.getLogger("django")


class RecycleBinListSerializer(serializers.ModelSerializer):
    delete_datetime = serializers.SerializerMethodField(method_name='get_delete_datetime')

    # currency = serializers.ReadOnlyField(source='currency.value)
    class Meta:
        model = RecycleBin
        fields = ['id', 'user_id', 'user_name', 'title', 'summary', 'from_table', 'relationship_no', 'delete_date',
                  'delete_datetime', ]

    def get_delete_datetime(self, obj):
        return obj.delete_date.strftime("%Y-%m-%d %H:%M:%S")


# class StStationInformationBaseApi(generics.CreateAPIView, generics.UpdateAPIView):
class RecycleBinList(APIView):
    """删除测站并放到回收站。注：Recycle是模块名，指代所属模块，不需要翻译，本接口语法由模块名+功能名构成"""
    params = None

    def get(self, request, *args, **kwargs):
        params = request.GET
        # 参数解析
        title = params.get('title', None)
        summary = params.get('summary', None)
        from_table = params.get('from_table', None)
        relationship_no = params.get('relationship_no', None)
        page = params.get('page', 1)
        size = params.get('size', 20)
        # where 条件筛选
        recycle_bin_set = RecycleBin.objects.filter()
        if title:
            recycle_bin_set = recycle_bin_set.filter(title__contains=title)
        if summary:
            recycle_bin_set = recycle_bin_set.filter(summary__contains=summary)
        if from_table:
            recycle_bin_set = recycle_bin_set.filter(from_table=from_table)
        if relationship_no:
            recycle_bin_set = recycle_bin_set.filter(relationship_no=relationship_no)
        # 分页
        recycle_bin_pager = Paginator(recycle_bin_set, size).page(page).object_list
        serializer = RecycleBinListSerializer(recycle_bin_pager, many=True)
        return Response({'err': 0, 'msg': 'OK', "data": {
            "list": serializer.data,
            "total": recycle_bin_set.count(),
        }}, status=status.HTTP_200_OK)
