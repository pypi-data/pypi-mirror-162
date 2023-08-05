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


class SubnetSpec(object):

    def __init__(self, az, vpcId, cidr, name, description, ipv6Cidr=None, secondaryCidr=None, secondaryCidrName=None):
        """
        :param az:  可用区, 如 cn-north-1a
        :param vpcId:  私有网络ID
        :param cidr:  子网的IPv4网络范围
        :param ipv6Cidr: (Optional) 子网的IPv6网络范围
        :param name:  名称
        :param description:  描述
        :param secondaryCidr: (Optional) 子网的次要cidr
        :param secondaryCidrName: (Optional) 子网的次要cidr名称
        """

        self.az = az
        self.vpcId = vpcId
        self.cidr = cidr
        self.ipv6Cidr = ipv6Cidr
        self.name = name
        self.description = description
        self.secondaryCidr = secondaryCidr
        self.secondaryCidrName = secondaryCidrName
