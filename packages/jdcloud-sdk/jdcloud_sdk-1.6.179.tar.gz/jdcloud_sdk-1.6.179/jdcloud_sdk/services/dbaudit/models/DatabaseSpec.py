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


class DatabaseSpec(object):

    def __init__(self, dbName=None, dbAddr=None, dbPort=None, dbType=None, dbVersion=None, username=None, password=None, dbDesc=None, dataMask=None, auditResponse=None):
        """
        :param dbName: (Optional) 数据库名称，库名,长度限制32字节,允许英文字母,数字,下划线,中划线和中文
        :param dbAddr: (Optional) 数据库地址, 可以是IP或域名，支持IPv6
        :param dbPort: (Optional) 数据库端口
        :param dbType: (Optional) 数据库类型: 
0->Oracle
1->SQLServer
2->DB2
3->MySQL
4->Cache
5->Sybase
6->DM7
7->Informix
9->人大金仓
10->Teradata
11->Postgresql
12->Gbase
16->Hive
17->MongoDB

        :param dbVersion: (Optional) 数据库版本
        :param username: (Optional) 用户名，SQLServer获取登录信息使用
        :param password: (Optional) 密码，SQLServer获取登录信息使用
        :param dbDesc: (Optional) 数据库的描述
        :param dataMask: (Optional) 是否对数据进行掩码
        :param auditResponse: (Optional) 是否对响应进行审计
        """

        self.dbName = dbName
        self.dbAddr = dbAddr
        self.dbPort = dbPort
        self.dbType = dbType
        self.dbVersion = dbVersion
        self.username = username
        self.password = password
        self.dbDesc = dbDesc
        self.dataMask = dataMask
        self.auditResponse = auditResponse
