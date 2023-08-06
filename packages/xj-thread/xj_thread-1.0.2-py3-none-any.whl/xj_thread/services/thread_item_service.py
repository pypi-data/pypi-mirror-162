# encoding: utf-8
"""
@project: djangoModel->thread_v2
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis:
@created_time: 2022/7/29 15:11
"""

from django.db import transaction

from xj_thread.serializers import ThreadDetailSerializer
from xj_thread.services.thread_statistic_service import StatisticsService
from .extend_service import InputExtend
from ..models import Thread
from ..models import ThreadExtendData
from ..utils.custom_response import util_response
from ..utils.model_handle import parse_model


# 信息服务CURD(支持扩展字段配置)  V2版本
class ThreadItemService:
    @staticmethod
    def detail(pk):
        """获取信息内容"""
        thread_obj = Thread.objects.filter(id=pk, is_deleted=False).first()
        if thread_obj:  # 信息统计表更新数据
            StatisticsService.increment(thread_id=thread_obj.id, tag='views', step=1)

        res_set = dict(ThreadDetailSerializer(thread_obj).data)
        # 扁平化数据
        res_set.update(res_set.pop('statistic'))
        res_set.update(res_set.pop('thread_extends'))
        return res_set, 0

    @staticmethod
    def edit(form_data, pk):
        extend_service = InputExtend(form_data)
        # 扩展字段与主表字段拆分
        form_data, extend_form_data = extend_service.transform_param()
        # 开启事务，防止脏数据
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                # 主表修改
                main_res = Thread.objects.filter(id=pk)
                if not main_res:
                    return util_response(err=5547, msg="数据不存在，无法进行修改")
                main_res.update(**form_data)
                # 扩展表修改或者创建
                if extend_form_data:
                    extend_res = ThreadExtendData.objects.filter(thread_id=pk)
                    if extend_res:
                        extend_res.update(**extend_form_data)
                    else:
                        form_data['thread_id'] = pk
                        extend_obj = ThreadExtendData(**form_data)
                        extend_obj.save()

                transaction.savepoint_commit(save_id)
            except Exception as e:
                transaction.rollback()
                return None, str(e)
        return None, None

    @staticmethod
    def delete(id):
        main_res = Thread.objects.filter(id=id, is_deleted=0)
        if not main_res:
            return None, "数据不存在，无法进行修改"
        main_res.update(is_deleted=1)
        return None, None

    @staticmethod
    def select_extend(id):
        """单独查询 查询扩展字段"""
        return util_response(parse_model(ThreadExtendData.objects.filter(id=id)))
