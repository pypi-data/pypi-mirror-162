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


class SendOutSiteNotice(object):

    def __init__(self, pin, notifyBusinessTypeEnum, templateId, templateParam, smsMessageSource, emailSubject=None, emailContent=None):
        """
        :param pin:  用户pin
        :param emailSubject: (Optional) 邮件标题
        :param emailContent: (Optional) 邮件内容
        :param notifyBusinessTypeEnum:  消息类型
        :param templateId:  模版code
        :param templateParam:  模版参数
        :param smsMessageSource:  业务编码(和产品申请)
        """

        self.pin = pin
        self.emailSubject = emailSubject
        self.emailContent = emailContent
        self.notifyBusinessTypeEnum = notifyBusinessTypeEnum
        self.templateId = templateId
        self.templateParam = templateParam
        self.smsMessageSource = smsMessageSource
