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


class UpdateQualityDetectionTemplateRequestObject(object):

    def __init__(self, template, modules=None):
        """
        :param template:  模板名称。长度不超过128个字符。UTF-8编码

        :param modules: (Optional) 检测项列表。取值范围：
  BlackScreen - 黑屏
  PureColor - 纯色
  ColorCast - 偏色
  FrozenFrame - 静帧
  Brightness - 亮度
  Contrast - 对比度

        """

        self.template = template
        self.modules = modules
