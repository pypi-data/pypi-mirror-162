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


class QuerySendStatusRequest(JDCloudRequest):
    """
    获取发送状态
    """

    def __init__(self, parameters, header=None, version="v2"):
        super(QuerySendStatusRequest, self).__init__(
            '/regions/{regionId}/querySendStatus', 'POST', header, version)
        self.parameters = parameters


class QuerySendStatusParameters(object):

    def __init__(self, regionId, appId, sequenceNumber, ):
        """
        :param regionId: Region ID
        :param appId: 应用ID
        :param sequenceNumber: 序列号
        """

        self.regionId = regionId
        self.appId = appId
        self.sequenceNumber = sequenceNumber
        self.phone = None

    def setPhone(self, phone):
        """
        :param phone: (Optional) 手机号
        """
        self.phone = phone

