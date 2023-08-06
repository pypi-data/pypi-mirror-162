# encoding: utf-8

from django.urls import path

from .view import BoundaryCreate, BoundaryUpdate, BoundaryDel, BoundaryList, BoundaryContainPoint
from .view import LocationGroupList, LocationGroupCreate, LocationGroupDel, LocationGroupUpdate
from .view import LocationUpdate, LocationCreate, LocationDel, LocationList

# 应用名称
app_name = 'location'

# 定位url
urlpatterns = [
    path('create/', LocationCreate.as_view()),  # 创建定位
    path('update/', LocationUpdate.as_view()),  # 修改定位
    path('list/', LocationList.as_view()),  # 定位点 分页条件查询
    path('del/', LocationDel.as_view()),  # 删除定位
]

# 定位分组CURD
urlpatterns += [
    path('group/list/', LocationGroupList.as_view()),  # 获取分组数据
    path('group/create/', LocationGroupCreate.as_view()),  # 获取分组数据
    path('group/delete/', LocationGroupDel.as_view()),  # 获取分组数据
    path('group/update/', LocationGroupUpdate.as_view()),  # 获取分组数据
]

# 边界URL
urlpatterns += [
    path('create/', BoundaryCreate.as_view()),
    path('update/', BoundaryUpdate.as_view()),
    path('del/', BoundaryDel.as_view()),
    path('list/', BoundaryList.as_view()),
    path('is_contain/', BoundaryContainPoint.as_view())  # 是否包含 定位点
]
