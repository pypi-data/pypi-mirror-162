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


class DisassociateElasticIpRequest(JDCloudRequest):
    """
    
为云主机解绑弹性公网IP。

详细操作说明请参考帮助文档：[解绑弹性公网IP](https://docs.jdcloud.com/cn/virtual-machines/disassociate-elastic-ip)

## 接口说明
- 该接口只支持解绑实例的主网卡的主内网IP上的弹性公网IP。

    """

    def __init__(self, parameters, header=None, version="v1"):
        super(DisassociateElasticIpRequest, self).__init__(
            '/regions/{regionId}/instances/{instanceId}:disassociateElasticIp', 'POST', header, version)
        self.parameters = parameters


class DisassociateElasticIpParameters(object):

    def __init__(self, regionId,instanceId,elasticIpId):
        """
        :param regionId: 地域ID。
        :param instanceId: 云主机ID。
        :param elasticIpId: 弹性公网IP的ID。
        """

        self.regionId = regionId
        self.instanceId = instanceId
        self.elasticIpId = elasticIpId

