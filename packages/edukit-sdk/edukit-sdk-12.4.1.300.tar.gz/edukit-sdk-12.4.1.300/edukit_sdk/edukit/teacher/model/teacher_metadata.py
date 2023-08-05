#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import json

from edukit_sdk.edukit.common.helpers.helpers import Helpers


class TeacherMetaData:
    def __init__(self):
        self._default_lang = None

    @property
    def default_lang(self):
        """
        :return: mixed
        """
        return self._default_lang

    @default_lang.setter
    def default_lang(self, default_lang):
        """
        课程的默认语言代码。说明如下：
        您可以提供多语言的教师信息；教育中心客户端向用户展示教师时，会优先匹配用户设备设置的系统语言。
        如您未提供用户系统语言对应的教师信息，将展示默认语言对应的数据
        语言代码由BCP-47定义，如简体中文为"zh-CN"，区分大小写（语言标识使用小写字母；区域名称使用大写字母）
        :param default_lang:
        :return:
        """
        self._default_lang = default_lang

    def to_json_string(self):
        return bytes(json.dumps(Helpers.change_object_to_array(self)),
                     encoding='utf-8')
