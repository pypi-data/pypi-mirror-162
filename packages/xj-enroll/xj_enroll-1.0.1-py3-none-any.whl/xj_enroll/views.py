from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from .models import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q
from django.db.models import F
import json

from django.http import JsonResponse


class EnrollAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = Enroll
        fields = '__all__'


class EnrollAPIView(APIView):
    permission_classes = (AllowAny,)
    params = None

    def get(self, request, format=None):
        self.params = request.query_params  # 返回QueryDict类型

        page = int(self.params['page']) - 1 if 'page' in self.params else 0
        size = int(self.params['size']) if 'size' in self.params else 10

        enrolls = Enroll.objects.all()\
            # .filter(Q(account=self.params['uid']) | Q(their_account=self.params['id'])).order_by('id')
        total = enrolls.count()
        now_pages = enrolls[page * size:page * size + size] if page >= 0 else enrolls
        data = now_pages.annotate(

        ).values(
            'id',
            'thread',
            'max',
            'price',
            'bid_mode',
            'ticket',
            'has_audit',
            'snapshot',
        )

        return Response({
            'err': 0,
            'msg': 'OK',
            'data': {'total': total, 'list': data, },
            'request': self.params,
            # 'serializer': serializer.data,
        })

    def post(self, request):
        self.params = request.query_params

        return Response({
            'err': 0,
            'msg': 'OK',
            'data': {},
            'request': self.params,
        })