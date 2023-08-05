# -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class LessonEditLocalizedData:
    def __init__(self):
        self._name = None  # 课程名称
        self._cover_id = None  # 横版封面图片的文件的素材id
        self._deeplink_url = None  # 从教育中心App跳转到您的App的DeepLink链接

    @property
    def name(self):
        """
        :return:mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        设置章节名称。
        对于每种已添加的语言类型，章节提交前必须指定此字段。后续更新时也要携带此字段。
        :param name:
        """
        self._name = name

    @property
    def cover_id(self):
        return self._cover_id

    @cover_id.setter
    def cover_id(self, cover_id):
        self._cover_id = cover_id

    @property
    def deeplink_url(self):
        """
        :return:mixed
        """
        return self._deeplink_url

    @deeplink_url.setter
    def deeplink_url(self, deeplink_url):
        """
        设置从教育中心客户端跳转到您的APP的DeepLink链接。
        如果用户需要跳转到您的APP（eduappUsed=false）学习此章节，在章节首次提交前必须提供此链接。如课程支持在教育中心学习，则此字段为可选。
        章节版本更新时可不携带此字段，此时将保留当前值不变。
        提供此字段时，需要同时提供residentAGApp字段，以便能正确拉起您的APP。
        此链接仅用于学习章节内容时跳转，如果用户购买课程时需要跳转到您的APP，应设置课程元数据中的deepLink参数。
        可以在此链接中增加必要的参数以辅助跳转后在您的APP内的逻辑处理，教育中心将透传这些参数。但请勿在链接中携带敏感数据（如用户密码等）。
        :param deeplink_url:
        """
        self._deeplink_url = deeplink_url

