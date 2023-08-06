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
import unittest
import os

from .itsm import ITSM


class TestITSM(unittest.TestCase):
    """
    测试itsm api接口调用
    """

    def setUp(self):
        self.app_code = os.getenv("APP_CODE")
        self.app_secret = os.getenv("APP_SECRET")
        self.bk_esb_url = os.getenv("BK_ESB_URL")
        self.itsm = ITSM(self.app_code, self.app_secret, self.bk_esb_url)

    def test_get_service_catalogs(self):
        is_success, message, data = self.itsm.client.get_service_catalogs(data={"project_key": "0"})
        self.assertEqual(is_success, True)

    def test_get_services(self):
        is_success, message, data = self.itsm.client.get_services(data={"catalog_id": 202})
        self.assertEqual(is_success, True)


if __name__ == '__main__':
    unittest.main()
