# encoding: utf-8
"""
@project: djangoModel->thread_v2
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/7/29 15:11
"""

from django.db import transaction

from ..models import Thread
from ..models import ThreadStatistic


# 统计服务
class StatisticsService:
    @staticmethod
    def increment(thread_id, tag, step=1):
        """
        增量计数
        :param thread_id:
        :param tag: 递增的字段
        :param step:  递增的步长
        :return: （err, data） 或者 util_response({'err': err, 'msg': msg, 'data': data})
        """
        query_obj = ThreadStatistic.objects.filter(thread_id=thread_id)
        match_data = query_obj.first()
        if match_data:
            form = {tag + "": getattr(match_data, tag) + int(step)}
            query_obj.update(**form)
        else:
            form = {"thread_id_id": thread_id, tag: step}
            ThreadStatistic.objects.create(**form)
        return None, 0

    @staticmethod
    def increments(thread_id, increment_dict, use_in_service=False):
        """
        批量计数增量统计
        :param thread_id:  关联主键
        :param increment_dict: {递增字段：递增的值}
        :param use_in_service: 是：否用在服务，是返回服务协议，否：返回响应对象
        :return:（err, data） 或者 util_response({'err': err, 'msg': msg, 'data': data})
        """
        is_set_thread = Thread.objects.filter(id=thread_id)
        if not is_set_thread:
            return None, '不存该条信息'
        # 事务回滚
        with transaction.atomic():
            sid = transaction.savepoint()
            try:
                for k, v in increment_dict.items():
                    StatisticsService.increment(thread_id, k, v, use_in_service)
                return None, 0
            except Exception as e:
                transaction.savepoint_rollback(sid)
                return None, "写入异常" + str(e)
