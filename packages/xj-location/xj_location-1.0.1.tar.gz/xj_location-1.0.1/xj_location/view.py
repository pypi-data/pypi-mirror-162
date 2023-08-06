# encoding: utf-8
"""
@project: djangoModel->api
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 逻辑拼装层
@created_time: 2022/5/31 17:21
"""
import json

from django.http import JsonResponse
from django.views.generic import View

from .models import Location, Boundary, LocationGroup
from .service.location_info_service import LocationInfoService
from .validate import CreatedValidate, GroupValidate
from .utils.custom_response import *


def parse_data(data):
    # 解析request对象 请求参数
    requestData = {}
    for k, v in data.items():
        requestData[k] = v if not v == "" else None
    return requestData


# ================ 定位操作 =====================
class LocationCreate(View):
    def post(self, request):
        service = LocationInfoService()
        return service.model_create(request, Location, CreatedValidate)


class LocationDel(View):
    def post(self, request):
        service = LocationInfoService()
        return service.model_del(request, Location, True)


class LocationUpdate(View):
    def post(self, request):
        # 修改定位
        try:
            requestData = parse_data(request.POST)
            if not 'id' in requestData.keys():
                return util_response("", 7557, status.HTTP_400_BAD_REQUEST, 'ID必填')
            res = Location.objects.filter(id=requestData['id'])
            if not res:
                return util_response("", 7557, status.HTTP_400_BAD_REQUEST, '该数据不存在')
            res.update(**requestData)
        except Exception as e:
            return util_response("", 7557, status.HTTP_400_BAD_REQUEST, e.__str__())
        return util_response("", 0, status.HTTP_200_OK, '修改成功')


class LocationList(View):
    def get(self, request):
        # 分页 条件 查询地位点
        service = LocationInfoService()
        return service.model_select(request, Location)


# ================ 定位分组CURD =====================
class LocationGroupList(View):
    def get(self, request):
        service = LocationInfoService()
        return service.model_select(request, LocationGroup)


class LocationGroupCreate(View):
    def post(self, request):
        service = LocationInfoService()
        return service.model_create(request, LocationGroup, GroupValidate)


class LocationGroupDel(View):
    def post(self, request):
        service = LocationInfoService()
        return service.model_del(request, LocationGroup)


class LocationGroupUpdate(View):
    def post(self, request):
        service = LocationInfoService()
        return service.model_update(request, LocationGroup)


# =============== 边界操作  ======================
class BoundaryCreate(View):
    def post(self, request):
        boundary_list = request.POST.get('boundary_list')
        name = request.POST.get('name')
        if not name or not boundary_list:
            return util_response("", 7588, status.HTTP_400_BAD_REQUEST, '参数错误')
        boundary_list = json.loads(boundary_list)
        Boundary.objects.create(boundary_list=boundary_list, name=name)
        return util_response("", 0, status.HTTP_200_OK, '添加成功')


class BoundaryUpdate(View):
    # 边界
    def post(self, request):
        id = request.POST.get('id')
        name = request.POST.get('name', "")
        boundary_list = request.POST.get('boundary_list')

        if boundary_list is None:
            boundary_list = ""
        else:
            boundary_list = json.loads(boundary_list)

        if not id:
            return util_response("", 8472, status.HTTP_400_BAD_REQUEST, 'ID不能为空')

        boundary_obj = Boundary.objects.filter(id=id)
        if not boundary_obj:
            return util_response("", 8472, status.HTTP_400_BAD_REQUEST, '数据不存在')
        boundary_obj.update(boundary_list=boundary_list, name=name)
        return util_response("", 0, status.HTTP_200_OK, '添加成功')


class BoundaryDel(View):
    def post(self, request):
        service = LocationInfoService()
        return service.model_del(request, Boundary)


class BoundaryList(View):
    def get(self, request):
        # 分页 条件 查询地位点
        service = LocationInfoService()
        return service.model_select(request, Boundary, False, 'boundary_list')


class BoundaryContainPoint(View):
    # 边界是否包含某个定位点
    def get(self, request):
        location_id = request.GET.get('location_id')
        boundary_id = request.GET.get('boundary_id')
        service = LocationInfoService()
        return service.boundary_contain_point(boundary_id, location_id)
