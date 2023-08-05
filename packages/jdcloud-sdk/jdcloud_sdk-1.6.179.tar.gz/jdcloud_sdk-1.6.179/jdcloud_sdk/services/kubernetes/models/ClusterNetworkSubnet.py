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


class ClusterNetworkSubnet(object):

    def __init__(self, subnetId=None, subnetType=None, enabled=None):
        """
        :param subnetId: (Optional) 子网 ID
        :param subnetType: (Optional) 子网类型，可取值为：pod_subnet/lb_subnet/node_subnet
        :param enabled: (Optional) 子网是否启用，仅pod子网可用。
        """

        self.subnetId = subnetId
        self.subnetType = subnetType
        self.enabled = enabled
