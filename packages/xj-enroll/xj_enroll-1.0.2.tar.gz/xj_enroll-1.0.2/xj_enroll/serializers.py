"""
Created on 2022-05-19
@author:刘飞
@description:报名模块序列化器
"""
from rest_framework import serializers
from .models import *


class EnrollListSerializer(serializers.ModelSerializer):
    """
    报名表序列化器
    """

    class Meta:
        model = Enroll
        fields = '__all__'


class EnrollRecordListSerializer(serializers.ModelSerializer):
    """
    报名记录列表序列化器
    """

    class Meta:
        model = EnrollRecord
        fields = '__all__'
