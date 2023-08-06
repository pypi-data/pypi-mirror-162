from django.contrib import admin

from .models import *


class TaskManager(admin.ModelAdmin):
    fields = ('title', 'summary', 'level', 'group', 'location', 'is_handle', 'price', 'cycle_day')
    list_display = ('title', 'summary', 'group', 'price')
    search_fields = ('title', 'summary', 'group', 'price')


class TaskGroupManager(admin.ModelAdmin):
    fields = ('title', 'description',)
    list_display = ('title', 'description',)
    search_fields = ('title', 'description',)


class TaskAppointManager(admin.ModelAdmin):
    fields = ('task', 'user', 'is_attend', 'leave_reason')
    list_display = ('id', 'task', 'user')


admin.site.register(Task, TaskManager)
admin.site.register(TaskGroup, TaskGroupManager)
admin.site.register(TaskAppoint, TaskAppointManager)

admin.site.site_header = 'msa一体化管理后台'
admin.site.site_title = 'msa一体化管理后台'
