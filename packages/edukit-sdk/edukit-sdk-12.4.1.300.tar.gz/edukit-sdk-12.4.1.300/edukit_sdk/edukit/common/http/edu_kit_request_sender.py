#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.

import logging

from edukit_sdk.edukit.common.auth.auth_token_credential import \
    AuthTokenCredential
from edukit_sdk.edukit.common.config.config import Config
from edukit_sdk.edukit.common.constant.client_constant import ClientConstant
from edukit_sdk.edukit.common.constant.http_constant import HttpConstant
from edukit_sdk.edukit.common.http.client import Client
from edukit_sdk.edukit.common.http.request import Request
from edukit_sdk.edukit.common.model.http_request_info import HttpRequestInfo


class EduKitRequestSender:
    def __init__(self, credential_list: dict):
        self._client = Client()
        config = Config()
        self._agent = config.get_config().get(
            ClientConstant.SDK_NAME) + '-' + config.get_config().get(
                ClientConstant.SDK_VERSION)
        self._domain = config.get_domain()
        self._credential_list = credential_list
        self._log_info_prefix = ClientConstant.REQUESTING

    def post(self, url, body=None, headers=None, form_data=None, params=None):
        """
        post请求
        :param url: 请求url
        :param body: 请求体
        :param headers: 请求头,如果传入为空,则默认为是application/json
        :param form_data: 非文件数据
        :param params:
        :return:
        """
        http_request_info = HttpRequestInfo(
            headers=headers, url=url, body=body,
            form_data=form_data, params=params)
        request = self.build_request(
            HttpConstant.REQUEST_METHOD_POST, http_request_info)
        logging.info("prefix:%s url:%s", self._log_info_prefix, request.url)
        return self._client.send_request(request)

    def put(self, url, body=None, headers=None):
        http_request_info = HttpRequestInfo(headers=headers, url=url,
                                            body=body)
        request = self.build_request(HttpConstant.REQUEST_METHOD_PUT,
                                     http_request_info)
        logging.info("prefix:%s url:%s", self._log_info_prefix, request.url)
        return self._client.send_request(request)

    def get(self, url, headers=None, body=None, params=None):
        http_request_info = HttpRequestInfo(headers=headers, url=url,
                                            body=body, params=params)
        request = self.build_request(
            HttpConstant.REQUEST_METHOD_GET, http_request_info)
        logging.info("prefix:%s url:%s", self._log_info_prefix, request.url)
        return self._client.send_request(request)

    def delete(self, url, headers=None, body=None):
        http_request_info = HttpRequestInfo(headers=headers, url=url,
                                            body=body)
        request = self.build_request(
            HttpConstant.REQUEST_METHOD_DELETE, http_request_info)
        logging.info("prefix:%s url:%s", self._log_info_prefix, request.url)
        return self._client.send_request(request)

    def upload_once(self, url, headers, body, method):
        return self._client.send_request(
            Request(url=url, method=method, headers=headers, body=body))

    def build_request(self, method, http_request_info: HttpRequestInfo):
        """
        @param method 请求方法
        @param http_request_info 请求class
        @return Request
        """
        auth_token_credential = AuthTokenCredential(self._credential_list)
        token = auth_token_credential.get_token()
        headers = http_request_info.headers
        url = http_request_info.url
        body = http_request_info.body
        form_data = http_request_info.form_data
        params = http_request_info.params
        if not headers:
            headers = dict()
        headers[HttpConstant.HEAD_AUTHORIZATION] = 'Bearer ' + token
        headers[HttpConstant.
                HEAD_CLIENT_ID] = auth_token_credential.get_client_id()
        headers[HttpConstant.HEAD_USER_AGENT] = self._agent
        if not headers.get(HttpConstant.CONTENT_TYPE):
            headers[HttpConstant.CONTENT_TYPE] = HttpConstant.APPLICATION_JSON
        url = self._domain + url

        return Request(url, method, headers, body, form_data, params)
