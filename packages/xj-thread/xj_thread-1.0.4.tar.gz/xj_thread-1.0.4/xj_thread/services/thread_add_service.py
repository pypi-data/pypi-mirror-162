# encoding: utf-8
"""
@project: djangoModel->thread_add
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 信息添加接口服务
@created_time: 2022/8/8 13:36
"""
from django.db import transaction

from xj_thread.models import ThreadExtendData, Thread, ThreadStatistic
from xj_thread.services.extend_service import InputExtend


class ThreadAddService:
    @staticmethod
    def add(params):
        # 扩展字段与主表字段拆分
        extend_service = InputExtend(params)
        form_data, extend_form_data = extend_service.transform_param()
        # 开启事务，防止脏数据
        with transaction.atomic():
            save_id = transaction.savepoint()
            try:
                instance = Thread.objects.create(**form_data)
                statistic_obj = ThreadStatistic(thread_id_id=instance.id)
                statistic_obj.save()
                if extend_form_data:  # 如果传扩展字段插入
                    extend_form_data['thread_id_id'] = instance.id
                    ThreadExtendData.objects.create(**extend_form_data)
                transaction.savepoint_commit(save_id)
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return None, str(e)
            return None, None
