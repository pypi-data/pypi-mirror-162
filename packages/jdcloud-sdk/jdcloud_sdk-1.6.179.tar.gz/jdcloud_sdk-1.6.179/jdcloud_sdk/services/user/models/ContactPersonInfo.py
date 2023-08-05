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


class ContactPersonInfo(object):

    def __init__(self, id=None, name=None, email=None, mobile=None, emailVerified=None, isPrimary=None, isOwner=None, createdTime=None, modifiedTime=None):
        """
        :param id: (Optional) 联系人ID(联系人为所有者时，该字段为0)
        :param name: (Optional) 联系人姓名
        :param email: (Optional) 邮箱
        :param mobile: (Optional) 手机号
        :param emailVerified: (Optional) 用户邮箱验证状态
        :param isPrimary: (Optional) 是否为主联系人
        :param isOwner: (Optional) 是否为账号所有者
        :param createdTime: (Optional) 创建时间
        :param modifiedTime: (Optional) 修改时间
        """

        self.id = id
        self.name = name
        self.email = email
        self.mobile = mobile
        self.emailVerified = emailVerified
        self.isPrimary = isPrimary
        self.isOwner = isOwner
        self.createdTime = createdTime
        self.modifiedTime = modifiedTime
