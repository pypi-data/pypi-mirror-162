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


class ModifyPortSetRequest(JDCloudRequest):
    """
    修改实例的端口库
    """

    def __init__(self, parameters, header=None, version="v1"):
        super(ModifyPortSetRequest, self).__init__(
            '/regions/{regionId}/instances/{instanceId}/portSets/{portSetId}', 'PATCH', header, version)
        self.parameters = parameters


class ModifyPortSetParameters(object):

    def __init__(self, regionId, instanceId, portSetId, portSetSpec):
        """
        :param regionId: 地域 Id, DDoS 防护包目前支持华北-北京, 华东-宿迁, 华东-上海
        :param instanceId: 防护包实例 Id
        :param portSetId: 端口库 Id
        :param portSetSpec: 添加实例的端口库请求参数
        """

        self.regionId = regionId
        self.instanceId = instanceId
        self.portSetId = portSetId
        self.portSetSpec = portSetSpec

