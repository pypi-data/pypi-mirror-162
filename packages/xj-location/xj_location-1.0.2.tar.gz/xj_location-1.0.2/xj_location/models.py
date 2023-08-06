"""
@project: djangoModel->base_service
@author: 孙楷炎
@created_time: 2022/5/31 17:50
"""
from django.db import models


class Location(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    region_code = models.BigIntegerField('行政ID', null=False, default=0)
    name = models.CharField('名称', null=False, default="", max_length=50)
    address = models.CharField('详细地址', null=False, default="", max_length=255)
    coordinate_type = models.IntegerField('定位类型', null=False, default=84)
    longitude = models.DecimalField('经度', null=False, max_digits=10, decimal_places=6)
    latitude = models.DecimalField('维度', null=False, max_digits=10, decimal_places=6)
    altitude = models.DecimalField('海拔', null=False, max_digits=10, decimal_places=6)
    user_id = models.IntegerField('用户ID', null=False, default=0)
    by_user_id = models.IntegerField('创建者ID', null=False, default=0)
    group_id = models.IntegerField('分组ID', null=False, default=0)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        managed = False
        db_table = "location_location"
        verbose_name = "定位信息表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class LocationGroup(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    group_name = models.CharField('分组名称', null=False, default="", max_length=50)
    description = models.CharField('描述', null=False, default="", max_length=255)

    class Meta:
        managed = False
        db_table = "location_group"
        verbose_name = "定位分组表"
        verbose_name_plural = verbose_name


class Boundary(models.Model):
    id = models.IntegerField(primary_key=True, null=False, auto_created=True)
    name = models.CharField('边界名称', null=False, default="", max_length=50)
    boundary_list = models.TextField('边界点列表', null=False, default="")
    created_at = models.DateTimeField('创建日期', null=False, auto_now_add=True)

    class Meta:
        managed = False
        db_table = "location_boundary"
        verbose_name = "定位边界"
        verbose_name_plural = verbose_name
