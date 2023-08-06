# _*_coding:utf-8_*_
import datetime
import json
import logging
import re

from django.db import connection

from ..models import RecycleBin

logger = logging.getLogger("django")


# class StStationInformationBaseApi(generics.CreateAPIView, generics.UpdateAPIView):
class RecycleService:
    # 删除测站并放到回收站。
    # 注1：Recycle是模块名，指代所属模块，不需要翻译，本接口语法由模块名+功能名构成
    # 注2：删除的索引值必须是主键值，且为int类型，如果表中没有主键或主键非int，则视为数据表设计者不接受还原功能。

    def __init__(self):
        pass

    @staticmethod
    def put_recycle_bin(table_name, target_id, primary_key='id', title_key=None, summary_format='',
                        relationship_no=None, user_id=None, user_name=None):
        """
        将一条数据放到回收站，但不删除
        @param table_name 目标表名
        @param target_id 目标表对就在的主键值
        @param primary_key 目标表的主键键名，默认为id
        @param title_key 指定title的键名
        @param summary_format 用于模糊搜索。开发者自定义内容，如：张三删除站码1003，站名陈家沟，位于河南省开封市的测站。在服务中通过自定义语法糖{{column_name}}来增强检索0的灵活性
        @param user_id 用户ID
        @param user_name 用户名
        """
        # 边界检查
        if not table_name:
            # print(u"错误，表名必填")
            return {'err': 1000, 'msg': u'错误，表名必填'}

        query_sql = "select * from {} where {} = {}".format(table_name, primary_key, target_id)
        # print("> put_recycle_bin: query_sql:", query_sql)
        cursor = connection.cursor()
        cursor.execute(query_sql)
        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        # 边界检查：数据存在且唯一
        if len(rows) == 0:
            return {'err': 1010, 'msg': "删除的数据不存在,表名：{}，ID：{}，主键：{}。".format(table_name, target_id, primary_key)}

        target_json = {}
        keys_map = {}
        # 将数据转为需要存储的数据
        for row in rows:
            for i, v in enumerate(row):
                # 序列化json不支持的对象，如时间、日期等
                if isinstance(v, datetime.datetime):
                    target_json[cols[i]] = v.strftime('%Y-%m-%d %H:%M:%S')
                    keys_map[cols[i]] = {'column_name': cols[i], 'type': 'datetime'}
                    continue
                elif isinstance(v, datetime.date):
                    target_json[cols[i]] = v.strftime("%Y-%m-%d")
                    keys_map[cols[i]] = {'column_name': cols[i], 'type': 'date'}
                    continue
                elif isinstance(v, datetime.time):
                    target_json[cols[i]] = v.strftime("%H:%M:%S")
                    keys_map[cols[i]] = {'column_name': cols[i], 'type': 'time'}
                    continue
                target_json[cols[i]] = v
            # 测试中文编码
            summary_match_keys = re.findall(r'{{(.*?)}}', summary_format)
            # 根据summary_format字段的{{}}语法糖格式化成摘要内容
            summary_eval = None
            if len(summary_match_keys) > 0:
                summary_eval = "'''" + re.sub('{{(.*?)}}', '{}', summary_format) + "'''.format(" + ', '.join(
                    ["target_json['" + key + "']" for key in summary_match_keys]) + ")"

            recycle_dict = {
                'user_id': user_id,
                'user_name': user_name,
                'title': target_json[title_key] if title_key else '',
                'summary': eval(summary_eval) if summary_eval else '',
                'from_table': table_name,
                'primary_key': primary_key,
                'target_id': target_id,
                'target_data': json.dumps(target_json, ensure_ascii=False),
                'keys_map': keys_map,
                'relationship_no': relationship_no,
            }
            recycle_set = RecycleBin(**recycle_dict)
            recycle_set.save()

    @staticmethod
    def restore_data(id=None, relationship_no=None, db_type="mysql"):
        """
        将一条数据从回收站还原到表中
        @param id 回收站的数据库表的id字段，只还原单条数据
        @param relationship_no 关联号，还原关联的所有数据，按id逆序进行还原
        :param db_type: mysqsl /sqlServer
        """
        # 边界检查
        if not id and not relationship_no:
            return {'err': 1000, 'msg': u'错误，缺少bin_id或relationship_no'}

        # print("> restore_data：", id, relationship_no)

        # 如果有关联号，则恢复所有相关的表数据
        if relationship_no:
            recycle_bin_set = RecycleBin.objects.filter(relationship_no=relationship_no)
        # 如果没有关联号，但有ID，则恢复单条数据
        if not relationship_no and id:
            recycle_bin_set = RecycleBin.objects.filter(id=id)

        if recycle_bin_set.count() == 0:
            return {'err': 1010, 'msg': u'找不到数据。'}

        # 开始还原每一条数据
        for it in recycle_bin_set:
            target_json = json.loads(it.target_data)
            recycle_values = [
                "'" + str(v.replace("'", "''")) + "\'" if isinstance(v, str) or isinstance(v, str) else 'NULL' if str(
                    v).lower() == 'none' else str(v) for k, v in target_json.items()]
            try:
                recycle_sql = "INSERT INTO `{}` ({}) VALUES ({});".format(it.from_table, ', '.join(
                    ['`' + key + '`' for key in target_json.keys()]), ', '.join(recycle_values))
                if db_type == 'sqlServer':
                    recycle_sql = "INSERT INTO [{}] ({}) VALUES ({})".format(it.from_table, ', '.join(
                        ['[' + key + ']' for key in target_json.keys()]), ', '.join(recycle_values))
                cursor = connection.cursor()
                if db_type == 'sqlServer':
                    cursor.execute("set identity_insert " + it.from_table + " ON")  # 允许向表中的标识列插入显式值
                cursor.execute(recycle_sql)
                if db_type == 'sqlServer':
                    cursor.execute("set identity_insert " + it.from_table + " OFF")  # 关闭向表中的标识列插入显式值
            except Exception as e:
                return {'err': 1030, 'msg': str(e), }
            # 数据恢复后记得从回收站删除
            it.delete()

        return {'err': 0, 'msg': u'OK', 'data': {'tip': u'成功！已恢复一条数据，数量：' + str(recycle_bin_set.count()) + ''}, }
