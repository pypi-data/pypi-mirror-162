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


class EnableAlarmsRequest(JDCloudRequest):
    """
    启用、禁用规则
    """

    def __init__(self, parameters, header=None, version="v2"):
        super(EnableAlarmsRequest, self).__init__(
            '/groupAlarms:switch', 'POST', header, version)
        self.parameters = parameters


class EnableAlarmsParameters(object):

    def __init__(self, alarmIds, ):
        """
        :param alarmIds: 告警规则的ID列表
        """

        self.alarmIds = alarmIds
        self.state = None

    def setState(self, state):
        """
        :param state: (Optional) 启用:1,禁用0,
        """
        self.state = state

