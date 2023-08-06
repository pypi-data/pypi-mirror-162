"""
Created on 2022-04-11
@description:刘飞
@description:发布子模块单挑数据删除/修改/详情
"""
from rest_framework.views import APIView

from xj_thread.services.thread_item_service import ThreadItemService
from xj_thread.utils.custom_authentication_wrapper import authentication_wrapper
from xj_thread.utils.model_handle import parse_data
from ..utils.custom_response import util_response

# class ThreadItemAPIView(APIView):
#     """
#     get: 信息表列表
#     post: 信息表新增
#     """
#
#     # @authentication_wrapper
#     def get(self, request, *args, **kwargs):
#         """查看单条信息"""
#         params = request.query_params
#         data, error_text = ThreadListService.list(params)
#         return util_response(data=data)
#
#     @authentication_wrapper
#     def post(self, request, *args, **kwargs):
#         """新增信息"""
#         request.data['user_id'] = request.user.get('user_id', None)
#         data, error_text = t.thread_list_create(request)
#         return util_response(data=data)

item_service = ThreadItemService()


class ThreadItemlAPI(APIView):
    """单挑信息处理，查，改，删"""

    def get(self, request, pk, *args, **kwargs):
        """信息表详情"""
        if not pk:
            return util_response(msg="非法请求", err=2554)
        data, error_text = item_service.detail(pk)

        if not error_text:
            return util_response(data=data)
        return util_response(err=47767, msg=error_text)

    @authentication_wrapper
    def put(self, request, pk, *args, **kwargs):
        """信息表编辑"""
        if not pk:
            return util_response(msg="非法请求", err=2554)
        form_data = parse_data(request=request, only_field=[
            'title', 'content', 'summary', 'ip', 'has_enroll', 'video', 'files', 'logs', 'price', 'author', 'classify_id', 'category_id',
            'auth_id', 'cover', 'show_id', 'hot_loop', 'hot_tip'
        ])
        data, error_text = item_service.edit(form_data, pk)
        if not error_text:
            return util_response()
        return util_response(err=47767, msg=error_text)

    @authentication_wrapper
    def delete(self, request, pk, *args, **kwargs):
        data, error_text = item_service.delete(pk)
        print(error_text)
        if not error_text:
            return util_response()
        return util_response(err=47767, msg=error_text)
