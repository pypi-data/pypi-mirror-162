"""
Created on 2022-05-19
@author:刘飞
@description:报名模块逻辑处理
"""

import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework import status
from apps.enroll.models import Enroll
from apps.enroll.serializers import EnrollListSerializer
from utils.custom_response import util_response

log = logging.getLogger()


class EnrollServices:
    def __init__(self):
        pass

    @staticmethod
    def enroll_list(request):
        if request.method == 'GET':
            size = request.query_params.get('size', 10)
            page = request.query_params.get('page', 1)
            enroll_obj = Enroll.objects.all()
            paginator = Paginator(enroll_obj, size)
            try:
                enroll_obj = paginator.page(page)
            except PageNotAnInteger:
                enroll_obj = paginator.page(1)
            except EmptyPage:
                enroll_obj = paginator.page(paginator.num_pages)
            except Exception as e:
                log.error(f'报名表分页:{str(e)}')
                return util_response(err=status.HTTP_400_BAD_REQUEST, msg=f'{str(e)}')
            res = EnrollListSerializer(enroll_obj, many=True)
            data = {'total': paginator.count, 'list': res.data}
            return util_response(data)
        elif request.method == 'POST':
            return util_response()
        else:
            return util_response(err=status.HTTP_405_METHOD_NOT_ALLOWED, msg='请求方式不允许！')

    @staticmethod
    def enroll_detail(request, pk):
        if request.method == 'DELETE':
            return util_response()
        else:
            return util_response(err=status.HTTP_405_METHOD_NOT_ALLOWED, msg='请求方式不允许！')
