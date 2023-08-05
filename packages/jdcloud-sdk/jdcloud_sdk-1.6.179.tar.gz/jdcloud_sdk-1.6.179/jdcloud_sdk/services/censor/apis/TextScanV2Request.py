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


class TextScanV2Request(JDCloudRequest):
    """
    文本同步检测-检测文本中是否包含违规信息
    """

    def __init__(self, parameters, header=None, version="v1"):
        super(TextScanV2Request, self).__init__(
            '/text:scanv2', 'POST', header, version)
        self.parameters = parameters


class TextScanV2Parameters(object):

    def __init__(self, ):
        """
        """

        self.bizType = None
        self.version = None
        self.checkLabels = None
        self.texts = None

    def setBizType(self, bizType):
        """
        :param bizType: (Optional) 业务bizType，请联系客户经理获取
        """
        self.bizType = bizType

    def setVersion(self, version):
        """
        :param version: (Optional) 接口版本号，固定值 v4
        """
        self.version = version

    def setCheckLabels(self, checkLabels):
        """
        :param checkLabels: (Optional) 可指定多个垃圾类别进行机器检测，多个垃圾类别以逗号分隔（"100,200"）
        """
        self.checkLabels = checkLabels

    def setTexts(self, texts):
        """
        :param texts: (Optional) 1-100条文本数据。
        """
        self.texts = texts

