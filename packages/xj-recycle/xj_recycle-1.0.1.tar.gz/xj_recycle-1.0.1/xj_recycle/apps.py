# _*_coding:utf-8_*_

from django.apps import AppConfig


class ResourceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.recycle'
    verbose_name = u'回收站系统'
