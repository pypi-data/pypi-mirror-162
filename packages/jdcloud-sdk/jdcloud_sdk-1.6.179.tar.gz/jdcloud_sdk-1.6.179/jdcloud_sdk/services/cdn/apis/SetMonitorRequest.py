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


class SetMonitorRequest(JDCloudRequest):
    """
    设置源站监控信息
    """

    def __init__(self, parameters, header=None, version="v1"):
        super(SetMonitorRequest, self).__init__(
            '/domain/{domain}/monitor', 'POST', header, version)
        self.parameters = parameters


class SetMonitorParameters(object):

    def __init__(self, domain,):
        """
        :param domain: 用户域名
        """

        self.domain = domain
        self.cycle = None
        self.monitorPath = None
        self.httpRequestHeader = None

    def setCycle(self, cycle):
        """
        :param cycle: (Optional) 探测周期，取值1和5，单位为分钟
        """
        self.cycle = cycle

    def setMonitorPath(self, monitorPath):
        """
        :param monitorPath: (Optional) 探测路径
        """
        self.monitorPath = monitorPath

    def setHttpRequestHeader(self, httpRequestHeader):
        """
        :param httpRequestHeader: (Optional) http请求头
        """
        self.httpRequestHeader = httpRequestHeader

