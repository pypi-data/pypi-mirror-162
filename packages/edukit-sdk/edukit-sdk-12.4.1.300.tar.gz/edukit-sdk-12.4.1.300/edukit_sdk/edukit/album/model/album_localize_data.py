# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.


class AlbumLocalizeData:
    def __init__(self):
        self._language = None
        self._name = None
        self._full_description = None
        self._cover_img_file_info = None
        self._landscape_cover_img_file_info = None

    @property
    def full_description(self):
        """
        :return:mixed
        """
        return self._full_description

    @full_description.setter
    def full_description(self, full_description):
        """
        专辑详细介绍。最大2000字符
        :param full_description:
        :return:
        """
        self._full_description = full_description


    @property
    def cover_img_file_info(self):
        """
        :return: mixed
        """
        return self._cover_img_file_info

    @cover_img_file_info.setter
    def cover_img_file_info(self, cover_img_file_info):
        """
        专辑封面图素材信息
        :param cover_img_file_info:
        :return:
        """
        self._cover_img_file_info = cover_img_file_info

    @property
    def language(self):
        """
        :return:mixed
        """
        return self._language

    @language.setter
    def language(self, language):
        """
        语言代码，由BCP-47定义，如简体中文为"zh-cn"
        :param language:
        :return:
        """
        self._language = language

    @property
    def landscape_cover_img_file_info(self):
        """
        :return:mixed
        """
        return self._landscape_cover_img_file_info

    @landscape_cover_img_file_info.setter
    def landscape_cover_img_file_info(self, landscape_cover_img_file_info):
        """
        专辑横版封面图素材信息
        :param landscape_cover_img_file_info:
        :return:
        """
        self._landscape_cover_img_file_info = landscape_cover_img_file_info

    @property
    def name(self):
        """
        :return:mixed
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        专辑名称。最大15字符
        :param name:
        :return:
        """
        self._name = name