#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.model.image_file_info import ImageFileInfo
from edukit_sdk.edukit.common.model.media_file_info import MediaFileInfo


class MediaLocalizedData:
    def __init__(self):
        self._media_type = None
        self._frame_image_file_info = None
        self._ordinal = None
        self._media_file_info = None

    @property
    def media_type(self):
        return self._media_type

    """
    * 媒体文件类型，定义如下，每次更新时必须携带此字段：
     * 1：课程介绍视频
     * 2：课程视频文件
     * 3：课程音频文件
     * 4：章节视频文件
     * 5：章节音频文件
     * 最小值 : 1
     * 最大值 : 5
     * 示例: 1
     * :param: mixed $mediaType
     * :return: MediaLocalizedData
    """

    @media_type.setter
    def media_type(self, media_type):
        self._media_type = media_type

    """
     * 媒体文件纵向分辨率。
     * 分辨率仅对视频类型媒体文件有意义，对于音频类型的媒体文件，此字段将被忽略。
     * 首次提交视频媒体文件时，必须提供此字段。更新媒体文件信息时，如果文件大小没有变化，可不携带此字段，此时将保留当前值不变。
     * 分辨率单位为像素。
     * 最小值 : 0
     * 最大值 : 9999示例: 1080
     * :param: mixed heigth
     * :return: MediaLocalizedData
    """

    @property
    def media_file_info(self):
        return self._media_file_info

    """
     * 媒体文件信息
     * :param: mixed media_file_info
     * :return: MediaLocalizedData
    """

    @media_file_info.setter
    def media_file_info(self, media_file_info: MediaFileInfo):
        self._media_file_info = media_file_info

    @property
    def frame_image_file_info(self):
        return self._frame_image_file_info

    """
     * 宣传海报图片文件信息
     * :param: mixed frame_image_file_info
     * :return: MediaLocalizedData
    """

    @frame_image_file_info.setter
    def frame_image_file_info(self, frame_image_file_info: ImageFileInfo):
        self._frame_image_file_info = frame_image_file_info

    @property
    def ordinal(self):
        return self._ordinal

    """
     * 媒体序号。
     * 序号用于教育中心App中展示多个同类视频时进行排序。
        当前一个课程中只有介绍视频支持提供多个，
        因此序号只对mediaType=1的课程介绍视频有意义。
     * 教育中心App会优先展示序号值较小的视频。
     * 最小值 : 0
     * 最大值 : 5
     * 示例: 2
     * :param: mixed ordinal
     * :return: MediaLocalizedData
    """

    @ordinal.setter
    def ordinal(self, ordinal):
        self._ordinal = ordinal
