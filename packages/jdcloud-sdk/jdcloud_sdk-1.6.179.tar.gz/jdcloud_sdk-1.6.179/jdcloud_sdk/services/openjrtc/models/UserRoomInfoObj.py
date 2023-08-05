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


class UserRoomInfoObj(object):

    def __init__(self, roomId=None, userRoomId=None, roomName=None, roomType=None, appId=None, createTime=None, updateTime=None):
        """
        :param roomId: (Optional) jrtc系统房间号
        :param userRoomId: (Optional) 业务接入方定义的且在JRTC系统内注册过的房间号
        :param roomName: (Optional) 房间名称
        :param roomType: (Optional) 房间类型 1-小房间(音频单流订阅) 2-大房间(音频固定订阅)
        :param appId: (Optional) appId
        :param createTime: (Optional) 创建时间
        :param updateTime: (Optional) 更新时间
        """

        self.roomId = roomId
        self.userRoomId = userRoomId
        self.roomName = roomName
        self.roomType = roomType
        self.appId = appId
        self.createTime = createTime
        self.updateTime = updateTime
