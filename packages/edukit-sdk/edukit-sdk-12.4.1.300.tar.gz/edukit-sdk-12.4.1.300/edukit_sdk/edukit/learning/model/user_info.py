# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2022-2022. All rights reserved.


class UserInfo:
    def __init__(self, user_id, user_id_type):
        self._user_id = user_id
        self._user_id_type = user_id_type


    @property
    def user_id(self):
        """
        :return:mixed
        """
        return self._user_id

    @user_id.setter
    def user_id(self, user_id):
        self._user_id = user_id

    @property
    def user_id_type(self):
        """
        :return:mixed
        """
        return self._user_id_type

    @user_id_type.setter
    def user_id_type(self, user_id_type):
        self._user_id_type = user_id_type

