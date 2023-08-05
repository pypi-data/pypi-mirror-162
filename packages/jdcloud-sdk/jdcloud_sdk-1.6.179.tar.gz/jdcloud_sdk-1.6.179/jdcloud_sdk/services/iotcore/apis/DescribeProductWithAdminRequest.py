# coding=utf8

# Copyright 2018 JDCLOUD.COM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# NOTE: This class is auto generated by the jdcloud code generator program.

from jdcloud_sdk.core.jdcloudrequest import JDCloudRequest


class DescribeProductWithAdminRequest(JDCloudRequest):
    """
    查看产品
    """

    def __init__(self, parameters, header=None, version="v2"):
        super(DescribeProductWithAdminRequest, self).__init__(
            '/regions/{regionId}/loongrayinstances/{instanceId}/products/{productKey}/admin', 'GET', header, version)
        self.parameters = parameters


class DescribeProductWithAdminParameters(object):

    def __init__(self, regionId, instanceId, productKey, ):
        """
        :param regionId: 地域ID
        :param instanceId: IoT Engine实例ID信息
        :param productKey: 产品Key
        """

        self.regionId = regionId
        self.instanceId = instanceId
        self.productKey = productKey

