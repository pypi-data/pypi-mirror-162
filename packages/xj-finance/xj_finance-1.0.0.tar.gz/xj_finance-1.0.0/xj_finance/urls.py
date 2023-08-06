#_*_coding:utf-8_*_
from django.urls import re_path
from django.conf.urls import static
from django.conf import settings


from apps.finance.apis.finance_transacts import FinanceTransacts
from apps.finance.apis.finance_transact import FinanceTransact
from apps.finance.apis.finance_pay_mode import FinancePayMode
# from apps.payment.apis.finance_pay import FinancePay
# from apps.payment.apis.finance_pay_test import FinanceTestPay
from apps.finance.apis.finance_currency import FinanceCurrency
from apps.finance.apis.finance_sand_box import FinanceSandBox
from apps.finance.apis.finance_contact_book import UserContactBook
from apps.finance.apis.finance_statistic import FinanceStatistic


urlpatterns = [
    re_path(r'^_transacts/?$', FinanceTransacts.as_view(), ),
    re_path(r'^_transact/?$', FinanceTransact.as_view(), ),
    re_path(r'^_pay_mode/?$', FinancePayMode.as_view(), ),
    # re_path(r'^_pay/?$', FinancePay.as_view(), ),
    # re_path(r'^_pay_test/?$', FinanceTestPay.as_view(), ),
    re_path(r'^_currency/?$', FinanceCurrency.as_view(), ),
    re_path(r'^_sand_box/?$', FinanceSandBox.as_view(), ),
    re_path(r'^_contact_book/?$', UserContactBook.as_view(), ),
    # re_path(r'^_export/?$', ExportExcel.as_view(), ),
    re_path(r'^_statistic/?$', FinanceStatistic.as_view(), ),

    # 该功能已使用finance_transact的POST方法代替
    # re_path(r'^_transact_add/?$', finance_transact_add.FinanceTransactAdd.as_view(), ),

    # 这里要填写/static/和/media/路径，否则django不会返回静态文件。
    re_path(
        "static/(?P<path>.*)$",
        static.serve,
        {"document_root": settings.STATIC_ROOT, "show_indexes": False},
        "static"
    ),
    re_path(
        "media/(?P<path>.*)$",
        static.serve,
        {"document_root": settings.MEDIA_ROOT, "show_indexes": False},
        "media"
    ),
]


