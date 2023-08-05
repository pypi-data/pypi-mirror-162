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


class DescribePhysicalBackupsRequest(JDCloudRequest):
    """
    查询所有的物理备份结果
    """

    def __init__(self, parameters, header=None, version="v2"):
        super(DescribePhysicalBackupsRequest, self).__init__(
            '/regions/{regionId}/backupPlans/{backupPlanId}:describePhysicalBackups', 'GET', header, version)
        self.parameters = parameters


class DescribePhysicalBackupsParameters(object):

    def __init__(self, regionId,backupPlanId,):
        """
        :param regionId: 地域代码，取值范围参见[《各地域及可用区对照表》]
        :param backupPlanId: 备份计划ID
        """

        self.regionId = regionId
        self.backupPlanId = backupPlanId
        self.pageNumber = None
        self.pageSize = None

    def setPageNumber(self, pageNumber):
        """
        :param pageNumber: (Optional) 显示数据的页码，默认为1，取值范围：[-1,∞)。pageNumber为-1时，返回所有数据页码；超过总页数时，显示最后一页
        """
        self.pageNumber = pageNumber

    def setPageSize(self, pageSize):
        """
        :param pageSize: (Optional) 每页显示的数据条数，默认为10，取值范围：[10,100]，且为10的整数倍
        """
        self.pageSize = pageSize

