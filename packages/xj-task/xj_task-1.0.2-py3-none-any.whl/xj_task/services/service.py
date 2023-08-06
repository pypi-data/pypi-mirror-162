# encoding: utf-8
"""
@project: djangoModel->service
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 任务模块服务封装
@created_time: 2022/6/7 11:55
"""

from ..models import Task, TaskGroup, TaskAppoint
from ..utils.model_handle import *
from ..validate import TaskValidator, GroupValidator, AppointValidator


class TaskService:
    @staticmethod
    def list(request):
        return model_select(request, Task)

    @staticmethod
    def add(request):
        return model_create(request, Task, TaskValidator)

    @staticmethod
    def delete(request):
        return model_delete(request, Task)

    @staticmethod
    def update(request):
        return model_update(request, Task)

    @staticmethod
    def appoint(request):
        # 任务绑定用户（指派，分配，抢单）
        data = parse_data(request)
        # 判断有效性
        validator = AppointValidator(data)
        is_pass, error = validator.validate()
        if not is_pass:
            return util_response("", 7557, error)
        # 去重
        res = parse_model(TaskAppoint.objects.filter(user_id=data['user_id'], task_id=data['task_id']))
        if not res is None:
            return util_response('', 4002, '该用户已分配，请勿重复分配')
        # 插入
        return model_create(request, TaskAppoint, None)

    @staticmethod
    def un_appoint(request):
        # 删除指派用户
        return model_delete(request, TaskAppoint)


class GroupService:
    @staticmethod
    def list(request):
        return model_select(request, TaskGroup, True)

    @staticmethod
    def add(request):
        return model_create(request, TaskGroup, GroupValidator)

    @staticmethod
    def delete(request):
        return model_delete(request, TaskGroup, False)

    @staticmethod
    def update(request):
        return model_update(request, TaskGroup, True)
