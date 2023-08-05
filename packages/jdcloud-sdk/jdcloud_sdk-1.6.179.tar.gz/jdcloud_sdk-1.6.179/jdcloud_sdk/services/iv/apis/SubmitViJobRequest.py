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


class SubmitViJobRequest(JDCloudRequest):
    """
    提交视频审查作业
    """

    def __init__(self, parameters, header=None, version="v1"):
        super(SubmitViJobRequest, self).__init__(
            '/viJobs:submit', 'POST', header, version)
        self.parameters = parameters


class SubmitViJobParameters(object):

    def __init__(self, templateId, region, ):
        """
        :param templateId: 视频审查模板ID
        :param region: 对象存储区域，输入和输入同区域
        """

        self.templateId = templateId
        self.region = region
        self.inputBucket = None
        self.inputFileKey = None
        self.outputBucket = None
        self.outputFilePath = None

    def setInputBucket(self, inputBucket):
        """
        :param inputBucket: (Optional) 输入空间
        """
        self.inputBucket = inputBucket

    def setInputFileKey(self, inputFileKey):
        """
        :param inputFileKey: (Optional) 输入文件
        """
        self.inputFileKey = inputFileKey

    def setOutputBucket(self, outputBucket):
        """
        :param outputBucket: (Optional) 输入空间
        """
        self.outputBucket = outputBucket

    def setOutputFilePath(self, outputFilePath):
        """
        :param outputFilePath: (Optional) 输入路径
        """
        self.outputFilePath = outputFilePath

