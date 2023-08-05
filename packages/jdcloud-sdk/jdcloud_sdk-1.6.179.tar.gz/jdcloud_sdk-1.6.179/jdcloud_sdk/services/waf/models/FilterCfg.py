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


class FilterCfg(object):

    def __init__(self, id=None, partOfReq=None, reqKey=None, matchLogic=None, reqValue=None, decodeFunc=None, isBase64Decode=None):
        """
        :param id: (Optional) 序号,不作更新使用
        :param partOfReq: (Optional) 请求位置 当匹配类型为"str"/"regex"/"size"时，可选字段：["headers"/"cookie"/"args"/"body"/"uri"/"method"] | 匹配类型为"SQLi"/"XSS"时:可选字段：["headers"/"cookie"/"args"/"body"/"uri"]|当匹配类型为"geo"/"ip"时，该字段为空
        :param reqKey: (Optional) 指定key，匹配类型为"geo"/"ip"时，该字段为空,|  partOfReq为uri/body/method 时，该字段为空，header/cookie时非空，args时选填
        :param matchLogic: (Optional) 匹配类型"str"时：["startsWith"/"endsWith"/"contains"/"equal"]|匹配类型为"geo"/"SQLi"/"XSS"/"regex"时：""|匹配类型为"size"时：["equal"/"notEquals"/"greaterThan"/"greaterThanOrEqual"/"lessThan"/"lessThanOrEqual"]
        :param reqValue: (Optional) // 匹配类型为"SQLi"/"XSS"时:""，匹配类型为"geo"时:该值为省份名称。匹配类型为"ip"时，该值为 ipv4/8/16/24/32)/ipv6/64 ipv6/128)| 匹配类型为"size"时:数字字符串 其他类型不限
        :param decodeFunc: (Optional) 仅type为str regex SQLi XSS时可非空，取值"","lowercase","trim","base64Decode","urlDecode","htmlDecode","hexDecode","sqlTrim"按先后顺序，多个时用 , 分隔
        :param isBase64Decode: (Optional) 不解码"base64Decode"解码,str时才有
        """

        self.id = id
        self.partOfReq = partOfReq
        self.reqKey = reqKey
        self.matchLogic = matchLogic
        self.reqValue = reqValue
        self.decodeFunc = decodeFunc
        self.isBase64Decode = isBase64Decode
