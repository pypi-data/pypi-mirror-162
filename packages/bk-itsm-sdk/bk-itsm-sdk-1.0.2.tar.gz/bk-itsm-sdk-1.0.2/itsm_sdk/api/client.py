# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making
蓝鲸智云-权限中心Python SDK(iam-python-sdk) available.
Copyright (C) 2017-2022 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
import json
from typing import Dict, List, Callable, Tuple

from ..exceptions import AuthAPIError
from .http import http_delete, http_get, http_post, http_put

logger = logging.getLogger("iam")


class Client(object):
    """
    itsm的client类，负责处理接口的调用
    """

    def __init__(
            self,
            app_code: str,
            app_secret: str,
            bk_esb_url: str = None,
            bk_apigateway_url: str = None
    ) -> None:
        """
        :param app_code: 应用code
        :param app_secret: 应用secret
        :param bk_esb_url: esb的url
        :param bk_apigateway_url: apigateway的url

        - 没有APIGateway的用法: Client(app_code, app_secret, bk_esb_url)
        - 有APIGateway的用法: Client(app_code, app_secret, bk_apigateway_url)
        """

        self._app_code = app_code
        self._app_secret = app_secret

        # 尽量使用apigateway
        self._apigateway_on = False
        if bk_apigateway_url:
            self._apigateway_on = True
            self._host = bk_apigateway_url.rstrip("/")
        else:
            if not bk_esb_url:
                raise AuthAPIError("init client fail, bk_esb_url or bk_apigateway_url should not be empty")

            self._esb_suffix = "/api/c/compapi"
            self._host = f"{bk_esb_url}/{self._esb_suffix}"

    def _call_api(
            self,
            http_func: Callable,
            host: str,
            path: str,
            data: Dict,
            headers: Dict,
            timeout: int = None
    ) -> Tuple[bool, str, Dict]:
        """
        - 调用api的基函数
        :param http_func: 回调的http函数
        :param host: url请求前缀
        :param path: url请求接口地址
        :param data: 请求体数据
        :param headers: 请求头数据
        :param timeout: 超时时间
        """

        url = f"{host}{path}"
        is_success, msg, rsp = http_func(url, data, headers=headers, timeout=timeout)

        if not is_success:
            return False, msg or "some unknown http errors occurred...", {}

        if rsp.get("code") != 0:
            return False, rsp.get("message") or "itsm api fail", {}

        rsp_data = rsp.get("data")
        return True, "success", rsp_data

    def _call_apigateway_api(
            self,
            http_func: Callable,
            path: str,
            data: Dict,
            timeout: int = None
    ) -> Tuple[bool, str, Dict]:
        """
        用apigateway进行api调用
        """

        # 封装应用鉴权信息到headers
        headers = {
            "X-Bkapi-Authorization": json.dumps({"bk_app_code": self._app_code, "bk_app_secret": self._app_secret})
        }
        return self._call_api(http_func, self._host, path, data, headers, timeout)

    def _call_esb_api(
            self,
            http_func: Callable,
            path: str,
            data: Dict,
            bk_token: str,
            bk_username: str,
            timeout: int = None
    ) -> Tuple[bool, str, Dict]:
        """
        用esb进行api的调用
        """

        # 封装鉴权信息
        headers = {}
        data.update(
            {
                "bk_app_code": self._app_code,
                "bk_app_secret": self._app_secret,
                "bk_token": bk_token,
                "bk_username": bk_username,
            }
        )
        return self._call_api(http_func, self._host, path, data, headers, timeout)

    def call_api(
            self,
            http_func: Callable,
            path: str,
            data: Dict,
            bk_token: str = None,
            bk_username: str = None,
            timeout: int = None
    ) -> Tuple[bool, str, Dict]:
        """
        api调用，根据host决定是esb调用还是apigw调用
        """

        if self._apigateway_on:
            return self._call_apigateway_api(http_func, path, data, timeout)

        return self._call_esb_api(http_func, path, data, bk_token, bk_username, timeout)

    def create_ticket(
            self,
            data: Dict,
            bk_token: str = None,
            bk_username: str = None
    ) -> Tuple[bool, str, Dict]:
        """
        创建单据
        """

        path = "/v2/itsm/create_ticket/"
        is_success, msg, result = self.call_api(http_post, path, data, bk_token, bk_username)
        return is_success, msg, result

    def ticket_approval_result(
            self,
            data: Dict,
            bk_token: str = None,
            bk_username: str = None
    ) -> Tuple[bool, str, Dict]:
        """
        审批结果查询
        """

        path = "/v2/itsm/ticket_approval_result/"
        is_success, msg, result = self.call_api(http_post, path, data, bk_token, bk_username)
        return is_success, msg, result

    def get_ticket_logs(
            self,
            data: Dict,
            bk_token: str = None,
            bk_username: str = None
    ) -> Tuple[bool, str, Dict]:
        """
        单据日志查询
        """

        path = "/v2/itsm/get_ticket_logs/"
        is_success, msg, result = self.call_api(http_get, path, data, bk_token, bk_username)
        return is_success, msg, result

    def get_service_catalogs(
            self,
            data: Dict,
            bk_token: str = None,
            bk_username: str = None
    ) -> Tuple[bool, str, Dict]:
        """
        服务目录查询
        """

        path = "/v2/itsm/get_service_catalogs/"
        is_success, msg, result = self.call_api(http_get, path, data, bk_token, bk_username)
        return is_success, msg, result

    def get_services(
            self,
            data: Dict,
            bk_token: str = None,
            bk_username: str = None
    ) -> Tuple[bool, str, Dict]:
        """
        服务列表查询
        """

        path = "/v2/itsm/get_services/"
        is_success, msg, result = self.call_api(http_get, path, data, bk_token, bk_username)
        return is_success, msg, result

    def create_service_catalog(
            self,
            data: Dict,
            bk_token: str = None,
            bk_username: str = None
    ) -> Tuple[bool, str, Dict]:
        """
        创建服务目录
        """

        path = "/v2/itsm/create_service_catalog/"
        is_success, msg, result = self.call_api(http_post, path, data, bk_token, bk_username)
        return is_success, msg, result

    def import_service(
            self,
            data: Dict,
            bk_token: str = None,
            bk_username: str = None
    ) -> Tuple[bool, str, Dict]:
        """
        导入服务
        """

        path = "/v2/itsm/import_service/"
        is_success, msg, result = self.call_api(http_post, path, data, bk_token, bk_username)
        return is_success, msg, result

    def update_service(
            self,
            data: Dict,
            bk_token: str = None,
            bk_username: str = None
    ) -> Tuple[bool, str, Dict]:
        """
        更新服务
        """

        path = "/v2/itsm/update_service/"
        is_success, msg, result = self.call_api(http_post, path, data, bk_token, bk_username)
        return is_success, msg, result
