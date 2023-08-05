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


class PanelMetric(object):

    def __init__(self, aggregator=None, downsample=None, metric=None, metricName=None, unit=None):
        """
        :param aggregator: (Optional) 推荐聚合方式
        :param downsample: (Optional) 推荐采样方式
        :param metric: (Optional) metric标识
        :param metricName: (Optional) metric名字
        :param unit: (Optional) 单位
        """

        self.aggregator = aggregator
        self.downsample = downsample
        self.metric = metric
        self.metricName = metricName
        self.unit = unit
