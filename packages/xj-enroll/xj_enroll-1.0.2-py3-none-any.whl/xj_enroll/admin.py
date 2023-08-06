from django.contrib import admin
from .models import Enroll
from .models import EnrollAuthStatus
from .models import EnrollPayStatus
from .models import EnrollRecord


class EnrollAdmin(admin.ModelAdmin):
    list_display = ('id', 'thread_id', 'max', 'price', 'bid_mode', 'ticket',
                    'hide_price', 'hide_user', 'has_repeat', 'has_vouch', 'has_audit', 'snapshot')
    search_fields = ('id', 'thread_id', 'max', 'price', 'bid_mode', 'ticket',
                     'hide_price', 'hide_user', 'has_repeat', 'has_vouch', 'has_audit', 'snapshot')
    fields = ('thread_id', 'max', 'price', 'bid_mode', 'ticket',
              'hide_price', 'hide_user', 'has_repeat', 'has_vouch', 'has_audit', 'snapshot')


class EnrollAuthStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')
    search_fields = ('id', 'value')
    fields = ('value',)


class EnrollPayStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'value')
    search_fields = ('id', 'value')
    fields = ('value',)


class EnrollRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'enroll_id', 'user_id', 'enroll_auth_status_id', 'enroll_pay_status_id',
                    'price', 'reply', 'remark')
    search_fields = ('id', 'enroll_id', 'user_id', 'enroll_auth_status_id', 'enroll_pay_status_id',
                     'price', 'reply', 'remark')
    fields = ('enroll_id', 'user_id', 'enroll_auth_status_id', 'enroll_pay_status_id',
              'price', 'reply', 'remark')


# Register your models here.
admin.site.register(Enroll, EnrollAdmin)
admin.site.register(EnrollAuthStatus, EnrollAuthStatusAdmin)
admin.site.register(EnrollPayStatus, EnrollPayStatusAdmin)
admin.site.register(EnrollRecord, EnrollRecordAdmin)
