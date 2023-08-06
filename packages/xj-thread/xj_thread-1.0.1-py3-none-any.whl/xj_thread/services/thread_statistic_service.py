# encoding: utf-8
"""
@project: djangoModel->thread_v2
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/7/29 15:11
"""

from django.core.paginator import Paginator
from django.db import transaction
from django.http import JsonResponse

from ..validator import ThreadInsertValidator
from .extend_service import InputExtend
from .extend_service import serializers_to_list
from ..models import Thread
from ..models import ThreadExtendData
from ..models import ThreadExtendField
from ..models import ThreadStatistic
from ..serializers import ThreadV2ListSerializer
from ..utils.custom_response import util_response
from ..utils.model_handle import parse_data
from ..utils.model_handle import parse_model



# 统计服务
class StatisticsService:
    @staticmethod
    def increment(thread_id, tag, step=1, use_in_service=False):
        """
        增量计数
        :param thread_id:
        :param tag: 递增的字段
        :param step:  递增的步长
        :param use_in_service: 是否使用在服务中
        :return: （err, data） 或者 util_response({'err': err, 'msg': msg, 'data': data})
        """
        query_obj = ThreadStatistic.objects.filter(thread_id=thread_id)
        match_data = query_obj.first()
        if match_data:
            form = {tag + "": getattr(match_data, tag) + int(step)}
            query_obj.update(**form)
        else:
            form = {"thread_id_id": thread_id, tag: step}
            print(form)
            ThreadStatistic.objects.create(**form)
        return StatisticsService.response(use_in_service)

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
            return StatisticsService.response(use_in_service=use_in_service, err=4588, msg='不存该条信息')
        # 事务回滚
        with transaction.atomic():
            sid = transaction.savepoint()
            try:
                for k, v in increment_dict.items():
                    StatisticsService.increment(thread_id, k, v, use_in_service)
                return StatisticsService.response(use_in_service=use_in_service)
            except Exception as e:
                transaction.savepoint_rollback(sid)
                return StatisticsService.response(use_in_service=use_in_service, err=2455, msg=str(e))

    # 返回格式化
    @staticmethod
    def response(use_in_service, err=0, msg="", data=None):
        if not use_in_service:
            return util_response({'err': err, 'msg': msg, 'data': data})
        else:
            if not err == 0:
                err = msg
            return err, data
