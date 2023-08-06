# _*_coding:utf-8_*_

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services.recycle_service import RecycleService

logger = logging.getLogger("django")


# class StStationInformationBaseApi(generics.CreateAPIView, generics.UpdateAPIView):
class RecycleBinRestore(APIView):
    # 删除测站并放到回收站。注：Recycle是模块名，指代所属模块，不需要翻译，本接口语法由模块名+功能名构成
    params = None

    def post(self, request, *args, **kwargs):
        params = self.params = request.POST
        print("> RecycleStationRestore: params:", params)
        id = params.get('id', None)
        relationship_no = params.get('relationship_no', None)

        result = RecycleService.restore_data(id=id, relationship_no=relationship_no)
        if result['err'] != 0:
            return Response({'err': result['err'], 'msg': result['msg'], "data": result.get('data', None), },
                            status=status.HTTP_200_OK)

        return Response({'err': 0, 'msg': result['msg'], "data": result['data'], }, status=status.HTTP_200_OK)
