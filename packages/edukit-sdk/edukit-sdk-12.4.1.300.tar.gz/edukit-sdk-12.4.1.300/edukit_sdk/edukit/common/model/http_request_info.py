#  -*- coding: utf-8 -*-
#  Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
import warnings


class HttpRequestInfo:
    def __init__(self,
                 headers=None,
                 url=None,
                 body=None,
                 form_data=None,
                 params=None):
        self._headers = headers
        self._url = url
        self._body = body
        self._form_data = form_data
        self._params = params

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers):
        self._headers = headers

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, body):
        self._body = body

    @property
    def form_data(self):
        return self._form_data

    @form_data.setter
    def form_data(self, form_data):
        self._form_data = form_data

    @property
    def params(self):
        return self._params

    @params.setter
    def params(self, params):
        self._params = params
