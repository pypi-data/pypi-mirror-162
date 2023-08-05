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


class CreateNetworkInterfaceRequest(JDCloudRequest):
    """
    创建网卡接口，只能创建辅助网卡
    """

    def __init__(self, parameters, header=None, version="v1"):
        super(CreateNetworkInterfaceRequest, self).__init__(
            '/regions/{regionId}/networkInterfaces/', 'POST', header, version)
        self.parameters = parameters


class CreateNetworkInterfaceParameters(object):

    def __init__(self, regionId,subnetId, ):
        """
        :param regionId: Region ID
        :param subnetId: 子网ID
        """

        self.regionId = regionId
        self.subnetId = subnetId
        self.az = None
        self.networkInterfaceName = None
        self.primaryIpAddress = None
        self.secondaryIpAddresses = None
        self.secondaryIpCount = None
        self.securityGroups = None
        self.sanityCheck = None
        self.description = None

    def setAz(self, az):
        """
        :param az: (Optional) 可用区，用户的默认可用区，该参数无效，不建议使用
        """
        self.az = az

    def setNetworkInterfaceName(self, networkInterfaceName):
        """
        :param networkInterfaceName: (Optional) 网卡名称，只允许输入中文、数字、大小写字母、英文下划线“_”及中划线“-”，不允许为空且不超过32字符。
        """
        self.networkInterfaceName = networkInterfaceName

    def setPrimaryIpAddress(self, primaryIpAddress):
        """
        :param primaryIpAddress: (Optional) 网卡主IP，如果不指定，会自动从子网中分配
        """
        self.primaryIpAddress = primaryIpAddress

    def setSecondaryIpAddresses(self, secondaryIpAddresses):
        """
        :param secondaryIpAddresses: (Optional) SecondaryIp列表
        """
        self.secondaryIpAddresses = secondaryIpAddresses

    def setSecondaryIpCount(self, secondaryIpCount):
        """
        :param secondaryIpCount: (Optional) 自动分配的SecondaryIp数量
        """
        self.secondaryIpCount = secondaryIpCount

    def setSecurityGroups(self, securityGroups):
        """
        :param securityGroups: (Optional) 要绑定的安全组ID列表，最多指定5个安全组
        """
        self.securityGroups = securityGroups

    def setSanityCheck(self, sanityCheck):
        """
        :param sanityCheck: (Optional) 源和目标IP地址校验，取值为0或者1,默认为1
        """
        self.sanityCheck = sanityCheck

    def setDescription(self, description):
        """
        :param description: (Optional) 描述,​ 允许输入UTF-8编码下的全部字符，不超过256字符
        """
        self.description = description

