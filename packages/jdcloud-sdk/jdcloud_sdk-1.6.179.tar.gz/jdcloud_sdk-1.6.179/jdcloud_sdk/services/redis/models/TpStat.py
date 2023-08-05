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


class TpStat(object):

    def __init__(self, ts=None, tp999=None, tp99=None, tp90=None, tp50=None, max=None, min=None, success=None, error=None, redirection=None):
        """
        :param ts: (Optional) 时间
        :param tp999: (Optional) TP999
        :param tp99: (Optional) TP99
        :param tp90: (Optional) TP90
        :param tp50: (Optional) TP50
        :param max: (Optional) 最大延时
        :param min: (Optional) 最小延时
        :param success: (Optional) 成功数
        :param error: (Optional) 错误数
        :param redirection: (Optional) 重定向数
        """

        self.ts = ts
        self.tp999 = tp999
        self.tp99 = tp99
        self.tp90 = tp90
        self.tp50 = tp50
        self.max = max
        self.min = min
        self.success = success
        self.error = error
        self.redirection = redirection
