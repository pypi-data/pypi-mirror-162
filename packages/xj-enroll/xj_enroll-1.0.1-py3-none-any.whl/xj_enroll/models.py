from django.db import models
# from apps.user.models import User
from apps.thread.models import Thread


class Enroll(models.Model):
    class Meta:
        db_table = 'eh_enroll'
        verbose_name_plural = '报名表'

    id = models.BigAutoField(verbose_name='ID', primary_key=True)
    thread_id = models.ForeignKey(verbose_name='信息ID', to=Thread, db_column='thread_id', related_name='+',
                                  on_delete=models.DO_NOTHING)
    max = models.IntegerField(verbose_name='限数', default=0)
    price = models.DecimalField(verbose_name='单价', max_digits=32, decimal_places=8, db_index=True, default=0)
    bid_mode = models.CharField(verbose_name='出价方式', max_length=255, blank=True, null=True)
    ticket = models.DecimalField(verbose_name='门票费', max_digits=32, decimal_places=2, db_index=True, default=0)

    hide_price = models.BooleanField(verbose_name='匿名价格')
    hide_user = models.BooleanField(verbose_name='匿名用户')
    has_repeat = models.BooleanField(verbose_name='重复报名')
    has_vouch = models.BooleanField(verbose_name='担保交易', default=True)

    has_audit = models.BooleanField(verbose_name='开启审核', default=True)
    snapshot = models.JSONField(verbose_name='快照', blank=True, null=True)

    def __str__(self):
        return f"{self.id}"


class EnrollAuthStatus(models.Model):
    class Meta:
        db_table = 'eh_enroll_auth_status'
        verbose_name_plural = '审核状态表'

    id = models.AutoField(verbose_name='ID', primary_key=True)
    value = models.CharField(verbose_name='值', max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.value}"


class EnrollPayStatus(models.Model):
    class Meta:
        db_table = 'eh_enroll_pay_status'
        verbose_name_plural = '支付状态表'

    id = models.AutoField(verbose_name='ID', primary_key=True)
    value = models.CharField(verbose_name='值', max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.value}"


class EnrollRecord(models.Model):
    class Meta:
        db_table = 'eh_enroll_record'
        verbose_name_plural = '报名记录表'

    id = models.BigAutoField(verbose_name='ID', primary_key=True)

    enroll_id = models.ForeignKey(verbose_name='报名ID', to=Enroll, db_column='enroll_id', related_name='+',
                                  on_delete=models.DO_NOTHING)
    # user_id = models.ForeignKey(verbose_name='用户ID', to=User, db_column='user_id', related_name='+', on_delete=models.DO_NOTHING)
    user_id = models.BigIntegerField(verbose_name='用户ID', db_index=True)
    enroll_auth_status_id = models.ForeignKey(verbose_name='审核状态ID', to=EnrollAuthStatus,
                                              db_column='enroll_auth_status_id',
                                              related_name='+', on_delete=models.DO_NOTHING)
    enroll_pay_status_id = models.ForeignKey(verbose_name='支付状态ID', to=EnrollPayStatus,
                                             db_column='enroll_pay_status_id',
                                             related_name='+', on_delete=models.DO_NOTHING)

    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    price = models.DecimalField(verbose_name='价格', max_digits=32, decimal_places=8, db_index=True, default=0)

    reply = models.JSONField(verbose_name='发起人答复', blank=True, null=True)
    remark = models.JSONField(verbose_name='备注', blank=True, null=True)

    def __str__(self):
        return f"{self.id}"
