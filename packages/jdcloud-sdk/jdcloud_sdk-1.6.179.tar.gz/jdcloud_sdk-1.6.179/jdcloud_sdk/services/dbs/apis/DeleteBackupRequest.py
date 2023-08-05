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


class DeleteBackupRequest(JDCloudRequest):
    """
    删除手动触发生成的备份文件
    """

    def __init__(self, parameters, header=None, version="v2"):
        super(DeleteBackupRequest, self).__init__(
            '/regions/{regionId}/backupPlans/{backupPlanId}/backup/{backupId}', 'DELETE', header, version)
        self.parameters = parameters


class DeleteBackupParameters(object):

    def __init__(self, regionId,backupPlanId,backupId,):
        """
        :param regionId: 地域代码，取值范围参见[《各地域及可用区对照表》]
        :param backupPlanId: 备份计划ID
        :param backupId: 备份文件ID
        """

        self.regionId = regionId
        self.backupPlanId = backupPlanId
        self.backupId = backupId

