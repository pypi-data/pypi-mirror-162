# _*_coding:utf-8_*_

from django.conf.urls import url

from .apis.recycle_bin_add import RecycleBinAddExample
from .apis.recycle_bin_list import RecycleBinList
from .apis.recycle_bin_restore import RecycleBinRestore

# 应用名称
app_name = 'recycle'

urlpatterns = [
    # 回收站模块
    url(r'bin_add/?$', RecycleBinAddExample.as_view(), name='RecycleStationRestore'),
    url(r'bin_list/?$', RecycleBinList.as_view(), name='RecycleBinList'),
    url(r'bin_restore/?$', RecycleBinRestore.as_view(), name='RecycleStationRestore'),
]
