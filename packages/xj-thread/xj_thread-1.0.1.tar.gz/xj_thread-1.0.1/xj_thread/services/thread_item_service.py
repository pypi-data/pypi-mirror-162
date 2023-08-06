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


# 信息服务CURD(支持扩展字段配置)  V2版本
class ThreadItemService:
    @staticmethod
    def add(request):
        form_data = parse_data(request)
        # 数据有效行判断（验证器）
        validator = ThreadInsertValidator(form_data)
        is_pass, error = validator.validate()
        if not is_pass:
            return util_response(err=4022, msg=error)
        # 扩展字段与主表字段拆分
        extend_service = InputExtend(form_data)
        form_data, extend_form_data = extend_service.transform_param()
        # 开启事务，防止脏数据 TODO 在这之前可以验证一下有效性
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                if extend_form_data:
                    extend_obj = ThreadExtendData.objects.create(**extend_form_data)
                    form_data['extend_id'] = extend_obj.id
                Thread.objects.create(**form_data)
                transaction.savepoint_commit(save_id)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return util_response(err=55447, msg=str(e))
        return util_response()

    @staticmethod
    def detail(request):
        """获取信息内容"""
        id = request.GET.get('id')
        if id is None:
            return JsonResponse({'err': 40225, 'msg': '参数错误', 'data': ''})
        res = parse_model(Thread.objects.filter(id=id).values('title', 'content', 'summary', 'cover', 'create_time'))
        # 查看计数自增1
        if res:
            StatisticsService.increment(thread_id=id, tag="views", step=1, use_in_service=True)
        return util_response(data=res)

    @staticmethod
    def edit(request):
        form_data = parse_data(request=request, except_field=['extend_id'])
        id = request.data.get('id', None)
        if id is None:
            return util_response(msg="ID 不能为空", err=2554)
        extend_service = InputExtend(form_data)
        # 扩展字段与主表字段拆分
        form_data, extend_form_data = extend_service.transform_param()
        # 开启事务，防止脏数据
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                # 主表修改
                main_res = parse_model(Thread.objects.filter(id=form_data['id']))
                if not main_res:
                    return util_response(err=5547, msg="数据不存在，无法进行修改")
                thread_id = form_data['id']
                extend_form_id = main_res[0]["extend"]
                del form_data['id']
                Thread.objects.filter(id=thread_id).update(**form_data)
                # 扩展表修改
                if extend_form_id:
                    extend_res = ThreadExtendData.objects.filter(id=extend_form_id)
                    if extend_res:
                        extend_res.update(**extend_form_data)
                transaction.savepoint_commit(save_id)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return util_response(err=75447, msg=str(e))
        return util_response()

    @staticmethod
    def delete(id):
        main_res = Thread.objects.filter(id=id)
        if not main_res:
            return util_response(err=5547, msg="数据不存在，无法进行修改")
        main_res.update(is_deleted=1)
        return util_response()


    @staticmethod
    def select_extend(id):
        """单独查询 查询扩展字段"""
        return util_response(parse_model(ThreadExtendData.objects.filter(id=id)))

