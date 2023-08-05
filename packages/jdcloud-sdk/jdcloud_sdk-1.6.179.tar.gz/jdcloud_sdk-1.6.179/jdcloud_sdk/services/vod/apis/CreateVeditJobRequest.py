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


class CreateVeditJobRequest(JDCloudRequest):
    """
    创建视频剪辑作业

    """

    def __init__(self, parameters, header=None, version="v1"):
        super(CreateVeditJobRequest, self).__init__(
            '/veditJobs', 'POST', header, version)
        self.parameters = parameters


class CreateVeditJobParameters(object):

    def __init__(self, projectName, timeline, ):
        """
        :param projectName: 工程名称
        :param timeline: 时间线信息
        """

        self.projectName = projectName
        self.description = None
        self.timeline = timeline
        self.mediaMetadata = None
        self.userData = None

    def setDescription(self, description):
        """
        :param description: (Optional) 工程描述
        """
        self.description = description

    def setMediaMetadata(self, mediaMetadata):
        """
        :param mediaMetadata: (Optional) 剪辑合成媒资元数据
        """
        self.mediaMetadata = mediaMetadata

    def setUserData(self, userData):
        """
        :param userData: (Optional) 用户数据，JSON格式的字符串。
在Timeline中的所有MediaClip中，若有2个或以上的不同MediaId，即素材片段来源于2个或以上不同视频，则在提交剪辑作业时，必须在UserData中指明合并后的视频画面的宽高。
如 {\"extendData\": {\"width\": 720, \"height\": 500}}，其中width和height必须为[16, 4096]之间的偶数
videoMode 支持 normal 普通模式 screen_record 屏幕录制模式 两种模式，默认为 normal。
如 "{\"extendData\":{\"videoMode\":\"screen_record\"}}"

        """
        self.userData = userData

