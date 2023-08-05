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


class AvailableResource(object):

    def __init__(self, architectureType=None, architectureName=None, recommended=None, soldOut=None, supportedMaxReplicas=None, supportedMinReplicas=None, supportedAzSpecifyType=None, minAzLimitForCluster=None, supportedExposeType=None, supportSmartProxy=None, availableEngineVersions=None):
        """
        :param architectureType: (Optional) 架构类型，目前支持：master-slave（标准版）、cluster（代理集群版）、native-cluster（cluster集群版）
        :param architectureName: (Optional) 架构类型名
        :param recommended: (Optional) 是否推荐
        :param soldOut: (Optional) 是否售罄
        :param supportedMaxReplicas: (Optional) 支持的最大副本数
        :param supportedMinReplicas: (Optional) 支持的最小副本数
        :param supportedAzSpecifyType: (Optional) 支持的AZ指定方式：SpecifyByReplicaGroup表示按副本组指定，SpecifyByCluster表示按整个集群指定
        :param minAzLimitForCluster: (Optional) 按集群指定AZ时，需要指定的最小AZ个数
        :param supportedExposeType: (Optional) 支持的外部访问方式：NodePort、LoadBalancer
        :param supportSmartProxy: (Optional) 是否支持SmartProxy
        :param availableEngineVersions: (Optional) 引擎版本列表
        """

        self.architectureType = architectureType
        self.architectureName = architectureName
        self.recommended = recommended
        self.soldOut = soldOut
        self.supportedMaxReplicas = supportedMaxReplicas
        self.supportedMinReplicas = supportedMinReplicas
        self.supportedAzSpecifyType = supportedAzSpecifyType
        self.minAzLimitForCluster = minAzLimitForCluster
        self.supportedExposeType = supportedExposeType
        self.supportSmartProxy = supportSmartProxy
        self.availableEngineVersions = availableEngineVersions
