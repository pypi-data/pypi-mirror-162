# -*- coding: utf-8 -*-
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

from edukit_sdk.edukit.common.errorcode.common_error_code import \
    CommonErrorCode
from edukit_sdk.edukit.common.helpers.helpers import Helpers
from edukit_sdk.edukit.common.http.edu_kit_request_sender import \
    EduKitRequestSender
from edukit_sdk.edukit.common.model.response import Response
from edukit_sdk.edukit.learning.impl.learning_handler import LearningHandler
from edukit_sdk.edukit.learning.model.user_info import UserInfo


class LearningReportRequest:
    @staticmethod
    def report_series_course_learning(user_info: UserInfo, course_id,
                                      lesson_id,
                                      series_course_learning_info,
                                      credential_list):
        user_id = user_info.user_id
        user_id_type = user_info.user_id_type
        response = Response()
        if Helpers.has_empty_param([user_id, course_id, user_id_type,
                                    lesson_id, series_course_learning_info]):
            response.result = Helpers.build_error_result(
                CommonErrorCode.PARAM_CANNOT_BE_EMPTY)
            return response
        learning_handler = LearningHandler(
            EduKitRequestSender(credential_list))

        return learning_handler.report_series_course_learning(
            user_id, course_id, user_id_type, lesson_id,
            series_course_learning_info)
