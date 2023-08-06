# encoding: utf-8
"""
@project: djangoModel->extend_service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 扩展服务
@created_time: 2022/7/29 15:14
"""

from ..models import ThreadExtendField, Thread
from ..utils.model_handle import *


class InputExtend:
    thread_extend_filed = None

    def __init__(self, form_data, need_all_field=False):
        """
        :param form_data: 表单
        :param need_all_field: 是否需要全部的扩展字段（查询的时候会用到）
        """
        self.form_data = form_data
        if form_data.get('classify_id', None):
            self.form_data['classify_id_id'] = self.form_data.pop('classify_id')
        if form_data.get('category_id', None):
            self.form_data['category_id_id'] = self.form_data.pop('category_id')

        if need_all_field:
            self.thread_extend_filed = parse_model(ThreadExtendField.objects.all())
            self.thread_extend_filed = {item["field"]: item["extend_field"] for item in self.thread_extend_filed if self.thread_extend_filed}
        else:
            # 新增或者修改的时候
            if "id" in self.form_data.keys():  # 修改时候：传了id,没有传classify_id
                thread = Thread.objects.filter(id=self.form_data.get('id')).first()
                self.thread_extend_filed = {
                    item["field"]: item["extend_field"]
                    for item in ThreadExtendField.objects.filter(classify_id=thread.classify_id).values('field', 'extend_field')
                }
            if self.form_data.get('category_id_id', None):
                self.thread_extend_filed = {
                    item["field"]: item["extend_field"]
                    for item in ThreadExtendField.objects.filter(classify_id=self.form_data.get('category_id_id')).values('field', 'extend_field')
                }

    # 请求参数转换
    def transform_param(self):
        # 没有定义扩展映射直接返回，不进行扩展操作
        if self.thread_extend_filed is None:
            return self.form_data, None
        extend_data = {self.thread_extend_filed[k]: self.form_data.pop(k) for k, v in self.form_data.copy().items() if k in self.thread_extend_filed.keys()}
        return self.form_data, extend_data
