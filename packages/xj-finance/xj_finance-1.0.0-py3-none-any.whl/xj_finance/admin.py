from django.contrib import admin

# 引入用户平台
from .models import PayMode, Currency, Transact, SandBox

# Register your models here.


class PayModeAdmin(admin.ModelAdmin):
    fields = ('pay_mode', )
    list_display = ('pay_mode', )
    search_fields = ('pay_mode', )


class CurrencyAdmin(admin.ModelAdmin):
    fields = ('currency', )
    list_display = ('currency', )
    search_fields = ('currency', )


class SandBoxAdmin(admin.ModelAdmin):
    fields = ('sand_box_name',)
    list_display = ('id', 'sand_box_name',)
    search_fields = ('id', 'sand_box_name',)


class TransactAdmin(admin.ModelAdmin):
    fields = ('transact_time', 'account', 'their_account', 'transact_id', 'platform', 'platform_order_id',
              'opposite_account', 'summary', 'currency', 'income', 'outgo', 'balance', 'pay_mode',
              'goods_info', 'pay_info', 'remark', 'images', 'sand_box')

    # list_display = ('transact_id', 'transact_time', 'account', 'their_account', 'platform', 'platform_order_id', 'sand_box', 'summary', 'currency', 'income', 'outgo', 'balance', 'pay_mode', 'remark')
    # list_display = ('transact_time', 'account', 'their_account', 'platform_order_id', 'currency', 'income', 'outgo', 'balance', 'pay_mode', 'remark')
    list_display = ('transact_time', 'account', 'their_account', 'income', 'outgo', 'balance', 'summary', 'sand_box')

    search_fields = ('user_name', 'full_name', 'phone')
    list_filter = ['platform', 'currency', 'account', 'their_account', 'platform_order_id']

    # def platform(self, obj):
    #     return obj.platform

    # 不起作用 https://docs.djangoproject.com/zh-hans/3.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
    # @admin.display(description='Name')
    # def transact_time(self, obj):
    #     return "2424"


admin.site.register(Transact, TransactAdmin)
admin.site.register(PayMode, PayModeAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(SandBox, SandBoxAdmin)
