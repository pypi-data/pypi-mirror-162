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
from apps.user.services import UserService

logger = logging.getLogger(__name__)


class FinanceSandBoxSerializer(serializers.ModelSerializer):
    value = serializers.ReadOnlyField(source='sand_box_name')
    sand_box = serializers.ReadOnlyField(source='sand_box_name')

    class Meta:
        model = SandBox
        fields = [
            # 'id',
            'value',
            'sand_box',
            'sand_box_name',
        ]


# 获取支付方式
class FinanceSandBox(generics.UpdateAPIView):  # 或继承(APIView)
    print("-" * 30, os.path.basename(__file__), "-" * 30)
    """ REST framework的APIView实现获取card列表 """
    # authentication_classes = (TokenAuthentication,)  # token认证
    # permission_classes = (IsAuthenticated,)   # IsAuthenticated 仅通过认证的用户
    permission_classes = (AllowAny,)  # 允许所有用户 (IsAuthenticated,IsStaffOrBureau)
    serializer_class = FinanceSandBoxSerializer
    params = None
    serializer_params = None

    def get(self, request, *args, **kwargs):
        sand_boxes = SandBox.objects.all()
        serializer = FinanceSandBoxSerializer(sand_boxes, many=True)
        return Response({
            'err': 0,
            'msg': 'OK',
            'data': serializer.data,
        })

    # 创建沙盒
    def post(self, request, *args, **kwargs):
        param = self.params = request.query_params  # 返回QueryDict类型
        item = self.serializer_params = {}

        # ========== 一、验证权限 ==========

        token = self.request.META.get('HTTP_AUTHORIZATION', '')
        if not token:
            return Response({'err': 4001, 'msg': '缺少Token', })
        user_id = UserService.checkToken(token)
        if not user_id:
            return Response({'err': 4002, 'msg': 'token验证失败', })

        # ========== 二、必填性检查 ==========
        if not param.get('sand_box_name', ''):
            return Response({'err': 3301, 'msg': '缺少sand_box_name', })

        # ========== 三、内容的类型准确性检查 ==========
        # 已经有的沙盒不用创建
        sand_box_name = param.get('sand_box_name', '')
        if sand_box_name:
            sand_box_set = SandBox.objects.filter(sand_box_name=sand_box_name).first()
            if sand_box_set is not None:
                return Response({'err': 1011, 'msg': 'sand_box_name已存在', })

        item['sand_box_name'] = sand_box_name

        print(">>> sand_box_name ", sand_box_name)
        print(">>> item ", item)

        # ================== 序列化入库 ========================
        # 增加一个记录
        serializer = FinanceSandBoxSerializer(data=item, context={})

        # 验证失败，获取错误信息
        if not serializer.is_valid():
            return Response({'err': 1018, 'msg': serializer.errors, })

        # 验证成功，获取数据
        # serializer.validated_data['sand_box'] = item['sand_box']

        serializer.save()

        return Response({
            'err': 0,
            'msg': '新增沙盒成功',
            # 'data': serializer.data,
        })

