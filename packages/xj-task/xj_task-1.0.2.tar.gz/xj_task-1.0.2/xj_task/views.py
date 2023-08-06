from rest_framework.views import APIView

from config.config import Config
from .services.service import GroupService, TaskService


# ==================== 任务 ====================
class TaskList(APIView):
    def get(self, request):
        print(Config.getIns().get('task', 'app_name','默认'))
        return TaskService.list(request)


class TaskAdd(APIView):
    def post(self, request):
        return TaskService.add(request)


class TaskDel(APIView):
    def post(self, request):
        return TaskService.delete(request)


class TaskUpdate(APIView):
    def post(self, request):
        return TaskService.update(request)


# ==================== 任务分组 ====================
class TaskGroupList(APIView):
    def get(self, request):
        return GroupService.list(request)


class TaskGroupAdd(APIView):
    def post(self, request):
        return GroupService.add(request)


class TaskGroupDel(APIView):
    def post(self, request):
        return GroupService.delete(request)


class TaskGroupUpdate(APIView):
    def post(self, request):
        return GroupService.update(request)


# ================== 任务分配 ======================
class TaskAppoint(APIView):
    def post(self, request):
        return TaskService.appoint(request)

    def un_appoint(self):
        return TaskService.un_appoint(self)
