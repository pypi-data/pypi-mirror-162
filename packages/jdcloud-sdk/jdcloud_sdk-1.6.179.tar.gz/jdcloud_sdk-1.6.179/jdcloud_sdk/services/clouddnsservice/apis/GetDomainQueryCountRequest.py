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


class GetDomainQueryCountRequest(JDCloudRequest):
    """
    查看主域名的解析次数
    """

    def __init__(self, parameters, header=None, version="v1"):
        super(GetDomainQueryCountRequest, self).__init__(
            '/regions/{regionId}/domain/{domainId}/queryCount', 'GET', header, version)
        self.parameters = parameters


class GetDomainQueryCountParameters(object):

    def __init__(self, regionId, domainId, domainName, start, end):
        """
        :param regionId: 实例所属的地域ID
        :param domainId: 域名ID，请使用getDomains接口获取。
        :param domainName: 查询的主域名，，请使用getDomains接口获取
        :param start: 查询时间段的起始时间, UTC时间，例如2017-11-10T23:00:00Z
        :param end: 查询时间段的终止时间, UTC时间，例如2017-11-10T23:00:00Z
        """

        self.regionId = regionId
        self.domainId = domainId
        self.domainName = domainName
        self.start = start
        self.end = end

