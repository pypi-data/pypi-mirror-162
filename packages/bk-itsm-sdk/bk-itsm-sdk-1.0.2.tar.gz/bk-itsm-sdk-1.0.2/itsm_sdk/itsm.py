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

from .api.client import Client


class ITSM(object):
    """
    ITSM调用接口类
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

        self.client = Client(app_code, app_secret, bk_esb_url, bk_apigateway_url)