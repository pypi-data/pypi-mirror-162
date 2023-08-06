# encoding: utf-8
"""
@project: djangoModel->config
@author: 孙楷炎
@Email: sky4834@163.com
@synopsis: 定位模块配置、常量文件
@created_time: 2022/5/31 17:21
"""

coordinate_type_value = {
    0: 'WGS84',
    84: 'WGS84(GPS)',
    2000: 'CGCS2000(国家)',
    80: 'WGS80(西安)',
    102: 'GCJ02(火星)'
}
coordinate_type_key = {
    'WGS84': 0,
    'WGS84(GPS)': 84,
    'CGCS2000(国家)': 2000,
    'WGS80(西安)': 80,
    'GCJ02(火星)': 102
}
