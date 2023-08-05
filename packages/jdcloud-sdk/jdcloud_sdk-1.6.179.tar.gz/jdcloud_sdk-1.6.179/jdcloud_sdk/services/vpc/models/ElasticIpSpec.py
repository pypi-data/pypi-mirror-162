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


class ElasticIpSpec(object):

    def __init__(self, bandwidthMbps, provider, chargeSpec=None):
        """
        :param bandwidthMbps:  弹性公网IP的限速（单位：Mbps），取值范围为[1-200]
        :param provider:  IP线路信息。当IP类型为标准公网IP时，取值为bgp或no_bgp，cn-north-1：bgp；cn-south-1：bgp；cn-east-1：bgp；cn-east-2：bgp。当IP类型为边缘公网IP时，其值可通过调用describeEdgeIpProviders、获取不同边缘节点的边缘公网IP线路信息
        :param chargeSpec: (Optional) 计费配置。边缘公网IP支持包年包月、按配置；标准公网IP支持包年包月、按配置、按流量
        """

        self.bandwidthMbps = bandwidthMbps
        self.provider = provider
        self.chargeSpec = chargeSpec
