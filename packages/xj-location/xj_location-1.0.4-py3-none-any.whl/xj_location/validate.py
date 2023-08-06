# encoding: utf-8
"""
@project: hydrology-station-python-4.0->validate
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 表单验证基类
@created_time: 2022/5/25 11:43
"""
import json

from django import forms


class Validate(forms.Form):
    """检验基类，子类编写规则，调用父类的validate方法"""

    def validate(self):
        """
        request 请求参数验证
        :return {'code': 'err': self.errors}:
        """
        if self.is_valid():
            return True, None
        else:
            error = json.dumps(self.errors)
            error = json.loads(error)
            temp_error = {}
            # 统一展示小写 提示，中文转义回来
            for k, v in error.items():
                temp_error[k.lower()] = v[0]
            return False, temp_error


class CreatedValidate(Validate):
    """验证查询表单"""
    region_code = forms.CharField(
        required=True,
        error_messages={
            "required": "行政编码 必填",
        })
    longitude = forms.CharField(
        required=True,
        error_messages={
            "required": "经度 必填",
        })
    latitude = forms.CharField(
        required=True,
        error_messages={
            "required": "维度 必填",
        })
    altitude = forms.CharField(
        required=True,
        error_messages={
            "required": "海拔 必填",
        })


class GroupValidate(Validate):
    group_name = forms.CharField(
        required=True,
        error_messages={
            "required": "code 必填",
        })
    description = forms.CharField(
        required=True,
        error_messages={
            "required": "description 必填",
        })
