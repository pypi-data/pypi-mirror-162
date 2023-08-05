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


class TransferTaskProgressInfo(object):

    def __init__(self, id=None, status=None, timeStart=None, succeedFileCount=None, failedFileCount=None):
        """
        :param id: (Optional) 任务ID
        :param status: (Optional) 运行状态
        :param timeStart: (Optional) 启动时间
        :param succeedFileCount: (Optional) 迁移成功文件个数
        :param failedFileCount: (Optional) 迁移失败文件个数
        """

        self.id = id
        self.status = status
        self.timeStart = timeStart
        self.succeedFileCount = succeedFileCount
        self.failedFileCount = failedFileCount
