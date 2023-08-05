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


class ClusterCreateSpec(object):

    def __init__(self, connectType, region, databaseType, clusterGid=None, name=None, host=None, port=None, accountName=None, password=None):
        """
        :param connectType:  接入类型 public, rds, ecs, gateway
        :param region:  地域
        :param databaseType:  数据库库类型：MySQL,Redis,TiDB 目前只支持MySQL
        :param clusterGid: (Optional) rds实例id，云数据库需要
        :param name: (Optional) 用户名，自建数据库需要
        :param host: (Optional) 主机域名，自建数据库需要
        :param port: (Optional) 端口号，自建数据库需要
        :param accountName: (Optional) 数据库账号，自建数据库需要
        :param password: (Optional) 数据库密码，自建数据库需要
        """

        self.connectType = connectType
        self.region = region
        self.databaseType = databaseType
        self.clusterGid = clusterGid
        self.name = name
        self.host = host
        self.port = port
        self.accountName = accountName
        self.password = password
