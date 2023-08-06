"""
Created on 2022-04-11
@description:刘飞
@description:发布子模块逻辑分发
"""
from rest_framework.views import APIView
from xj_user.utils.custom_authorization import CustomAuthentication

from ..services.thread_list_service import ThreadListService
from ..utils.custom_authentication_wrapper import authentication_wrapper
from ..utils.custom_response import util_response


class ThreadItemAPIView(APIView):
    """
    get: 信息表列表
    post: 信息表新增
    """

    # authentication_classes = (CustomAuthentication,)

    # @authentication_wrapper
    def get(self, request, *args, **kwargs):
        params = request.query_params
        # params: page, size, filter
        data, error_text = ThreadListService.list(params)
        return util_response(data=data)

    @authentication_wrapper
    def post(self, request, *args, **kwargs):
        request.data['user_id'] = request.user.get('user_id', None)
        data, error_text = t.thread_list_create(request)
        return util_response(data=data)
