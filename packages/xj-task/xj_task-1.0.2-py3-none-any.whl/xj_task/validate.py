# encoding: utf-8
"""
@project: djangoModel->validate
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 表单验证器
@created_time: 2022/7/6 9:59
"""
from django import forms

from .utils.validate import Validate


# 任务
class TaskValidator(Validate):
    title = forms.CharField(
        required=True,
        error_messages={
            "required": "标题 必填",
        })
    summary = forms.CharField(
        required=True,
        error_messages={
            "required": "摘要 必填",
        })


# 指派
class AppointValidator(Validate):
    task_id = forms.IntegerField(
        required=True,
        error_messages={
            "required": "task_id 必填",
        })
    user_id = forms.IntegerField(
        required=True,
        error_messages={
            "required": "user_id 必填",
        })


class GroupValidator(Validate):
    title = forms.CharField(
        required=True,
        error_messages={
            "required": "title 必填",
        }
    )