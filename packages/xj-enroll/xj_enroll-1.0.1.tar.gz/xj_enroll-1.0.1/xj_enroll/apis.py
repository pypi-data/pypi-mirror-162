"""
Created on 2022-05-19
@author:刘飞
@description:报名模块逻辑分发
"""
from rest_framework.views import APIView
from apps.enroll.services import EnrollServices
from apps.user.utils.custom_authorization import CustomAuthentication

e = EnrollServices()


class EnrollRecordListView(APIView):
    """
    get:报名记录列表
    post:报名记录新增
    """
    authentication_classes = (CustomAuthentication,)

    def get(self, request):
        res = e.enroll_list(request)
        return res

    def post(self, request):
        res = e.enroll_list(request)
        return res
