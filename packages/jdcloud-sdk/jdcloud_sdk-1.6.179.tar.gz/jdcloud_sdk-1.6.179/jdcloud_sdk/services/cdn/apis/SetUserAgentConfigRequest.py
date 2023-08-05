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


class SetUserAgentConfigRequest(JDCloudRequest):
    """
    设置userAgent信息
    """

    def __init__(self, parameters, header=None, version="v1"):
        super(SetUserAgentConfigRequest, self).__init__(
            '/domain/{domain}/userAgentConfig', 'POST', header, version)
        self.parameters = parameters


class SetUserAgentConfigParameters(object):

    def __init__(self, domain,):
        """
        :param domain: 用户域名
        """

        self.domain = domain
        self.userAgentType = None
        self.userAgentList = None

    def setUserAgentType(self, userAgentType):
        """
        :param userAgentType: (Optional) userAgent类型,取值：block（黑名单）,allow（白名单）,默认为block
        """
        self.userAgentType = userAgentType

    def setUserAgentList(self, userAgentList):
        """
        :param userAgentList: (Optional) UA列表,如果userAgentList为空,则为全部删除
        """
        self.userAgentList = userAgentList

