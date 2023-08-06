# _*_coding:utf-8_*_

import os, logging, time, json, copy
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import response
from rest_framework import serializers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Q
from django.db.models import F

from ..models import *

logger = logging.getLogger(__name__)


class FinanceCurrencySerializer(serializers.ModelSerializer):
    value = serializers.ReadOnlyField(source='currency')

    class Meta:
        model = Currency
        fields = [
            # 'id',
            'value',
            'currency',
        ]


# 获取支付方式
class FinanceCurrency(generics.UpdateAPIView):  # 或继承(APIView)
    """ REST framework的APIView实现获取card列表 """
    # authentication_classes = (TokenAuthentication,)  # token认证
    # permission_classes = (IsAuthenticated,)   # IsAuthenticated 仅通过认证的用户
    permission_classes = (AllowAny,)  # 允许所有用户 (IsAuthenticated,IsStaffOrBureau)
    serializer_class = FinanceCurrencySerializer
    params = None

    def get(self, request, *args, **kwargs):
        self.params = request.query_params  # 返回QueryDict类型

        currencies = Currency.objects.all()
        serializer = FinanceCurrencySerializer(currencies, many=True)
        return Response({
            'err': 0,
            'msg': 'OK',
            'data': serializer.data,
        })