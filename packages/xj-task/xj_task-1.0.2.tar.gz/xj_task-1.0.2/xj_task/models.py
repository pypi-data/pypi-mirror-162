from django.db import models

from xj_location.models import Location
from xj_user.models import BaseInfo


# 任务分组
class TaskGroup(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    title = models.CharField(verbose_name='任务标题', max_length=50, blank=True, null=True, )
    description = models.CharField(verbose_name='分组描述', max_length=255, blank=True, null=True, )
    is_delete = models.BooleanField(verbose_name='是否删除', blank=True, null=True, default=0)

    class Meta:
        db_table = 'task_group'
        verbose_name_plural = "任务-任务分组"

    def __str__(self):
        return f"{self.title}"


# 任务主表
class Task(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    title = models.CharField(verbose_name='任务标题', max_length=50, blank=True, null=True, )
    summary = models.CharField(verbose_name='任务摘要', max_length=255, blank=True, null=True, )
    level = models.IntegerField(verbose_name='任务等级', blank=True, null=True, default=0)
    group = models.ForeignKey(TaskGroup, null=True, blank=True, on_delete=models.CASCADE, verbose_name='分组')
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.CASCADE, verbose_name='定位')
    is_handle = models.IntegerField(verbose_name='是否处理', blank=True, null=True, default=0)
    price = models.BigIntegerField(verbose_name='金额（分）', blank=True, null=True, default=0)
    end_time = models.IntegerField(verbose_name='日期', blank=True, null=True, default=0)
    cycle_day = models.IntegerField(verbose_name='任务周期', blank=True, null=True, default=0)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'task'
        verbose_name_plural = "任务-任务详情"


# 任务派发表
class TaskAppoint(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.CASCADE, verbose_name='任务')
    user = models.ForeignKey(BaseInfo, null=True, blank=True, on_delete=models.CASCADE, verbose_name='用户')
    is_attend = models.BooleanField(verbose_name='是否出席', blank=True, null=True, default=0)
    leave_reason = models.IntegerField(verbose_name='请假原因', blank=True, null=True, default=0)

    class Meta:
        db_table = 'task_appoint'
        verbose_name_plural = "任务-任务指派"
