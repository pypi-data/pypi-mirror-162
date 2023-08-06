# _*_coding:utf-8_*_

from django.db import models


class RecycleBin(models.Model):
    # 回收站模块（删除还原功能）
    id = models.AutoField(primary_key=True, auto_created=True)
    user_id = models.BigIntegerField('用户ID', blank=True, null=True, )
    user_name = models.CharField('用户名', max_length=255, blank=True, null=True)
    title = models.CharField('回收标题', max_length=255, blank=True, null=True, db_index=True)  # 数据标题。用于搜索
    summary = models.CharField('回收摘要', max_length=255, blank=True, null=True,
                               db_index=True)  # 摘要。用于模糊搜索。开发者自定义内容，如：张三删除站码1003，站名陈家沟，位于河南省开封市的测站
    from_table = models.CharField('回收来源表', max_length=128)
    primary_key = models.CharField('回收主键', max_length=128)  # 目标表的主键
    target_id = models.BigIntegerField('主键值', blank=False)
    target_data = models.TextField('备份数据', blank=False)  # 目标数据。删除时的回收数据区，json<object>结构
    keys_map = models.TextField('key关联', blank=True,
                                null=True)  # 键映射。还原时的数据映射，当数据库字段和target_data中不一致时使用，json<key-value>结构c
    relationship_no = models.BigIntegerField('释放标识', blank=True, null=True)
    # 关联号。当同一任务需要删除关联的多表或多条数据时，使用该值标识其为同一任务。注：当多条数据恢复依赖顺序时（如外键约束等）则根据id逆序回滚操作。
    delete_date = models.DateTimeField('回收日期', auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'recycle_bin'
        verbose_name = "回收站表"
        verbose_name_plural = verbose_name
