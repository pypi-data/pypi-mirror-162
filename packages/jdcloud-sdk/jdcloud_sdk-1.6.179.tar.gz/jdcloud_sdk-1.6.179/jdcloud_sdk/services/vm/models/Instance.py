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


class Instance(object):

    def __init__(self, instanceId=None, instanceName=None, hostname=None, instanceType=None, vpcId=None, subnetId=None, privateIpAddress=None, elasticIpId=None, elasticIpAddress=None, status=None, description=None, imageId=None, systemDisk=None, dataDisks=None, primaryNetworkInterface=None, secondaryNetworkInterfaces=None, launchTime=None, az=None, keyNames=None, charge=None, ag=None, faultDomain=None, tags=None, chargeOnStopped=None, policies=None, dedicatedPoolId=None, dedicatedHostId=None, burstInfo=None, resourceGroupId=None):
        """
        :param instanceId: (Optional) 云主机ID。
        :param instanceName: (Optional) 云主机名称。
        :param hostname: (Optional) 云主机hostname。
        :param instanceType: (Optional) 实例规格。
        :param vpcId: (Optional) 主网卡所属VPC的ID。
        :param subnetId: (Optional) 主网卡所属子网的ID。
        :param privateIpAddress: (Optional) 主网卡主内网IP地址。
        :param elasticIpId: (Optional) 主网卡主IP绑定弹性IP的ID。
        :param elasticIpAddress: (Optional) 主网卡主IP绑定弹性IP的地址。
        :param status: (Optional) 云主机状态，参考 [云主机状态](https://docs.jdcloud.com/virtual-machines/api/vm_status)。
        :param description: (Optional) 云主机描述。
        :param imageId: (Optional) 云主机使用的镜像ID。
        :param systemDisk: (Optional) 系统盘配置。
        :param dataDisks: (Optional) 数据盘配置列表。
        :param primaryNetworkInterface: (Optional) 主网卡主IP关联的弹性公网IP配置。
        :param secondaryNetworkInterfaces: (Optional) 辅助网卡配置列表。
        :param launchTime: (Optional) 云主机实例的创建时间。
        :param az: (Optional) 云主机所在可用区。
        :param keyNames: (Optional) 云主机使用的密钥对名称。
        :param charge: (Optional) 云主机的计费信息。
        :param ag: (Optional) 云主机关联的高可用组，如果创建云主机使用了高可用组，此处可展示高可用组名称。
        :param faultDomain: (Optional) 高可用组中的错误域。
        :param tags: (Optional) Tag信息。
        :param chargeOnStopped: (Optional) 停机不计费模式。该参数仅对按配置计费且系统盘为云硬盘的实例生效，并且不是专有宿主机中的实例。
`keepCharging`：关机后继续计费。
`stopCharging`：关机后停止计费。

        :param policies: (Optional) 自动任务策略，关联了自动任务策略时可获取相应信息。
        :param dedicatedPoolId: (Optional) 云主机所属的专有宿主机池。
        :param dedicatedHostId: (Optional) 云主机所属的专有宿主机ID。
        :param burstInfo: (Optional) 突发型实例参数信息
        :param resourceGroupId: (Optional) 资源组ID
        """

        self.instanceId = instanceId
        self.instanceName = instanceName
        self.hostname = hostname
        self.instanceType = instanceType
        self.vpcId = vpcId
        self.subnetId = subnetId
        self.privateIpAddress = privateIpAddress
        self.elasticIpId = elasticIpId
        self.elasticIpAddress = elasticIpAddress
        self.status = status
        self.description = description
        self.imageId = imageId
        self.systemDisk = systemDisk
        self.dataDisks = dataDisks
        self.primaryNetworkInterface = primaryNetworkInterface
        self.secondaryNetworkInterfaces = secondaryNetworkInterfaces
        self.launchTime = launchTime
        self.az = az
        self.keyNames = keyNames
        self.charge = charge
        self.ag = ag
        self.faultDomain = faultDomain
        self.tags = tags
        self.chargeOnStopped = chargeOnStopped
        self.policies = policies
        self.dedicatedPoolId = dedicatedPoolId
        self.dedicatedHostId = dedicatedHostId
        self.burstInfo = burstInfo
        self.resourceGroupId = resourceGroupId
