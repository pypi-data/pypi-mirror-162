# encoding: utf-8
"""
@project: djangoModel->thread_v2
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/7/29 15:11
"""

import logging

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
from ..models import ThreadTagMapping
from ..serializers import ThreadListSerializer
from ..utils.custom_response import util_response
from ..utils.model_handle import parse_data
from ..utils.model_handle import parse_model

log = logging.getLogger()


# 信息服务CURD(支持扩展字段配置)  V2版本
class ThreadListService:
    @staticmethod
    def list(params):
        page = params.get('page', 1)
        size = params.get('size', 20)

        tag_id_list = params.get('tag_id_list') if params.get('tag_id_list') else None  # 列表[1,2,3,4]
        tag_value_list = params.get('tags', '').split(',')  # 列表['同城', '圣诞节']查询不用这个
        
        exclude_category_list = params.get('exclude_categorys').split(',') if params.get('exclude_categorys') else None
        # print("exclude_category_list:", exclude_category_list)

        # 边界检查：时间格式验证
        start_time = params.get('start_time')
        end_time = params.get('end_time')
        try:
            if start_time:
                datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            if end_time:
                datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise serializers.ValidationError(f'时间格式错误:它的格式应该是YYYY-MM-DD HH:MM:SS')

        # 允许进行过渡的字段条件
        conditions = {
            "category_id": params.get('category_id'),
            "category_id__value": params.get('category_value'),
            "classify_id": params.get('classify_id'),
            "classify_id__value": params.get('classify_value'),
            "title__icontains": params.get('title'),
            "content__icontains": params.get('content'),
            "create_time__gte": params.get('start_time'),
            "create_time__lte": params.get('end_time'),
            "user_id": params.get('user_id'),
            "is_deleted": False,
        }
        conditions = {k: v for k, v in conditions.items() if v or v is False}
        # print("> conditions:", conditions)

        # 边界检查，不写这行，当size为0时，页面会报分母不能为零
        if int(size) <= 0:
            raise serializers.ValidationError(f'请求每页数量(size)不能为零。')

        # 另一个条件查询的生成语句
        # keys = 'category_id__value classify_id classify_id__value title__icontains content__icontains create_time__gte create_time__lte is_deleted user_id'.split()
        # values = [category_value, classify_id, classify_value, title, content, start_time, end_time, is_deleted, user_id]
        # conditions = {k: v for k, v in zip(keys, values) if v or v is False}

        # 开始按过滤条件
        try:
            thread_set = Thread.objects.filter(**conditions)
        except Exception as e:
            return util_response(err=7557, msg=e.__str__())

        # 指定不需要过滤的类别字段
        if exclude_category_list:
            thread_set = thread_set.exclude(category_id__in=exclude_category_list)

        count = thread_set.count()

        # 这里先处理标签查询
        if tag_id_list:
            try:
                thread_id_list = ThreadTagMapping.objects.filter(tag_id__in=tag_id_list).values_list('thread_id', flat=True)  # flat转列表形式
                thread_set = thread_set.filter(id__in=thread_id_list)
            except ValueError as e:
                log.error(f'信息表标签查询{e}')
                pass

        # 分页数据
        page_set = ThreadListSerializer(Paginator(thread_set, size).get_page(page), many=True)
        res = final_res = page_set.data

        for it in final_res:
            it.update(it.pop('statistic'))
            it.update(it.pop('thread_extends'))

        return {'data': final_res, 'size': int(size), 'page': int(page), 'count': count}, None


    @staticmethod
    def select_extend(id):
        """单独查询 查询扩展字段"""
        return util_response(parse_model(ThreadExtendData.objects.filter(id=id)))

