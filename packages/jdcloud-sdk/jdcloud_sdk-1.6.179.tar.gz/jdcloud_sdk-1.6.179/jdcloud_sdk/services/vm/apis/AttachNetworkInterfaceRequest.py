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


class AttachNetworkInterfaceRequest(JDCloudRequest):
    """
    
为云主机绑定弹性网卡。

详细操作说明请参考帮助文档：[绑定弹性网卡](https://docs.jdcloud.com/cn/virtual-machines/attach-eni)

## 接口说明
- 实例状态必须为 `running` 或 `stopped` 状态，同时实例没有正在进行中的任务时才可以操作。
- 实例中的主网卡是不可以解绑和绑定的，绑定弹性网卡只支持绑定辅助网卡。
- 目标弹性网卡上如果绑定了弹性公网IP，那么其所在的可用区需要与云主机的可用区保持一致，或者弹性公网IP是全可用区类型的，才允许绑定该弹性网卡。
- 弹性网卡与云主机必须在相同vpc下。
- 对于受管网卡，授权中不能含有 `instance-attach` 用户才可以挂载。
- 对于授信网卡，授权中必须含有 `instance-attach` 用户才可以挂载。
- 实例挂载弹性网卡的数量，不能超过实例规格的限制。可查询 [DescribeInstanceTypes](https://docs.jdcloud.com/virtual-machines/api/describeinstancetypes) 接口获得指定规格可挂载弹性网卡的数量上限。

    """

    def __init__(self, parameters, header=None, version="v1"):
        super(AttachNetworkInterfaceRequest, self).__init__(
            '/regions/{regionId}/instances/{instanceId}:attachNetworkInterface', 'POST', header, version)
        self.parameters = parameters


class AttachNetworkInterfaceParameters(object):

    def __init__(self, regionId,instanceId,networkInterfaceId, ):
        """
        :param regionId: 地域ID。
        :param instanceId: 云主机ID。
        :param networkInterfaceId: 弹性网卡ID。
        """

        self.regionId = regionId
        self.instanceId = instanceId
        self.networkInterfaceId = networkInterfaceId
        self.autoDelete = None

    def setAutoDelete(self, autoDelete):
        """
        :param autoDelete: (Optional) 随云主机实例自动删除，默认为False。
受管网卡或授信网卡默认为False并且不支持修改。

        """
        self.autoDelete = autoDelete

