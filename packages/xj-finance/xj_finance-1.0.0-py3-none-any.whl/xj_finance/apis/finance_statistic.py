# _*_coding:utf-8_*_

import os, logging, time, json, copy
import re
from datetime import datetime, timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import response
from rest_framework import serializers
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum, Count
from decimal import Decimal
import pytz
from django.http import HttpResponse
from django.utils.translation import gettext as _

from ..models import Transact, SandBox, Currency
from apps.user.services import UserService
from apps.finance.services import FinanceService

logger = logging.getLogger(__name__)


class FinanceStatistic(generics.UpdateAPIView):  # 或继承(APIView)
    """ REST framework的APIView实现获取card列表 """
    # authentication_classes = (TokenAuthentication,)  # token认证
    # permission_classes = (IsAuthenticated,)   # IsAuthenticated 仅通过认证的用户
    permission_classes = (AllowAny,)  # 允许所有用户 (IsAuthenticated,IsStaffOrBureau)
    # serializer_class = FinanceTransactsSerializer
    params = None  # 请求体的原始参数

    print("-" * 30, os.path.basename(__file__), "-" * 30)

    def get(self, request, *args, **kwargs):
        param = self.params = request.query_params  # 返回QueryDict类型

        # ========== 一、验证权限 ==========

        token = self.request.META.get('HTTP_AUTHORIZATION', '')
        if not token:
            return Response({'err': 4001, 'msg': '缺少Token', })

        user_id = UserService.checkToken(token)
        if not user_id:
            return Response({'err': 4002, 'msg': 'token验证失败', })

        # ========== 二、必填性检查 ==========

        # ========== 三、内容的类型准确性检查 ==========

        transacts = Transact.objects.filter(Q(account=user_id))

        # 准备查询语句，按币种查询
        by_currency_query = {}  # 所有数据统计查询语句
        for it in Currency.objects.all():
            outgo_key = it.currency.lower() + '_outgo'
            income_key = it.currency.lower() + '_income'
            if not transacts.filter(currency__currency=it.currency).count():
                continue
            by_currency_query.update({
                outgo_key: Sum('outgo', filter=Q(currency__currency=it.currency)),
                income_key: Sum('income', filter=Q(currency__currency=it.currency)),
            })

        # 所有数据统计
        all_aggregate = transacts.aggregate(**by_currency_query)
        all_aggregate['count'] = transacts.count()

        # 真实交易数据统计
        non_sand_box = transacts.filter(sand_box__isnull=True)
        real_aggregate = non_sand_box.aggregate(**by_currency_query)
        real_aggregate['count'] = non_sand_box.count()

        # annotate_dict = transacts.annotate(count_sand_box=Count('sand_box', distinct=True)).values('account', 'sand_box', 'count_sand_box')
        # print("> anno_dict:", annotate_dict)

        sand_box_aggregate = []
        sand_box_set = SandBox.objects.all()
        currency_set = Currency.objects.all()
        for group in sand_box_set:
            item = {'sand_box': group.sand_box_name}
            group_set = transacts.filter(sand_box__sand_box_name=group.sand_box_name)
            for it in currency_set:
                outgo_key = it.currency.lower() + '_outgo'
                income_key = it.currency.lower() + '_income'
                aggr_eval = {
                    outgo_key: Sum('outgo', filter=Q(currency__currency=it.currency)),
                    income_key: Sum('income', filter=Q(currency__currency=it.currency)),
                }
                temp_dict = group_set.aggregate(**aggr_eval)

                # print('> temp_dict:', temp_dict)
                # 没有的数据就没必要写进去了
                if not temp_dict[outgo_key] and not temp_dict[income_key]:
                    # print('> temp_dict in:', temp_dict[key_outgo] and temp_dict[key_income])
                    continue
                # print('> temp_dict has:', temp_dict[key_outgo], temp_dict[key_income])

                item.update(temp_dict)

            # print('> item.keys():', item.keys())
            # 没有的数据就没必要写进去了
            if len(item.keys()) == 1:
                continue
            item['count'] = group_set.count()
            sand_box_aggregate.append(item)

        print(">>> sand_box_set: ", sand_box_set)

        print(">>> param: ", param)

        platform_name = param.get('platform', '')
        if platform_name:
            FinanceService.transact_filter(param_name=platform_name, obj_list=transacts)


        # ========== 四、相关前置业务逻辑处理 ==========

        # ========== 五、翻页 ==========


        return Response({
            'err': 0,
            'msg': 'OK',
            'data': {
                'all': all_aggregate,
                'test': [
                    {
                        'currency': 'CNY',
                        'sand_box': 'best',
                        'currency_label': '人民币',
                        'income': 0,
                        'outgo': 0,
                        'balance': 0,
                        'unit': '元',
                        'count': 0,
                    },
                ],
                'real': real_aggregate,
                'sand_box': sand_box_aggregate,
            },
        })

