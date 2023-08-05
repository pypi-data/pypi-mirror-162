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


class DataSource(object):

    def __init__(self, id=None, ip=None, port=None, dbName=None, modifiedBy=None, status=None, userName=None, passwd=None, passwdEcrypt=None, cdsCluster=None, dbType=None, createTime=None, environmentType=None, dbTypeName=None, sensitivity=None, userType=None, mongoAuth=None, schemaCname=None, schemaDepartment=None, schemaDba=None, schemaOwner=None, isStandard=None, coldict=None, version=None, schemaEnvironment=None, query=None, region=None, addrMode=None, addrOrigin=None, addrKey=None, extra=None):
        """
        :param id: (Optional) 主键id。
        :param ip: (Optional) 数据库ip地址。
        :param port: (Optional) 数据库端口。
        :param dbName: (Optional) dbName，数据库名称，RDS或DRDS实例时为空。
        :param modifiedBy: (Optional) 修改用户。
        :param status: (Optional) 0为有效，1为无效。
        :param userName: (Optional) 数据库用户名。
        :param passwd: (Optional) 数据库密码。
        :param passwdEcrypt: (Optional) 数据库加密密码。
        :param cdsCluster: (Optional) Cds集群名称。
        :param dbType: (Optional) 数据库类型，CDS("CDS", 1), MYSQL("MYSQL", 2), ORACLE("ORACLE", 3), SQLSERVER("SQLSERVER", 4), CDSMYSQL("CDSMYSQL", 5), CDSORACLE("CDSORACLE", 6), CDSSQLSERVER("CDSSQLSERVER", 7), DATACENTER("DATACENTER", 8), HBASE("Hbase",9),MONGODB("MongoDb",10),ES("ES",11), MYSQL_INS("MYSQL_INS",12), DRDS_INS("DRDS_INS",13),STARDB_INS("STARDB_INS",14), STARDB_PROXY_INS("STARDB_PROXY_INS",15);。
        :param createTime: (Optional) 创建时间。
        :param environmentType: (Optional) 环境类型，已废弃。
        :param dbTypeName: (Optional) 已废弃。
        :param sensitivity: (Optional) 已废弃。
        :param userType: (Optional) 已废弃。
        :param mongoAuth: (Optional) mongo权限类型。
        :param schemaCname: (Optional) 数据库中文名备注，已废弃。
        :param schemaDepartment: (Optional) 数据库所属部门，已废弃。
        :param schemaDba: (Optional) 数据库维护dba，已废弃。
        :param schemaOwner: (Optional) 数据库owner，已废弃。
        :param isStandard: (Optional) 已废弃。
        :param coldict: (Optional) 已废弃。
        :param version: (Optional) 数据库版本，已废弃。
        :param schemaEnvironment: (Optional) 数据库环境，已废弃。
        :param query: (Optional) 已废弃。
        :param region: (Optional) 数据库所属区域。
        :param addrMode: (Optional) 地址模式：CLASSIC("CLASSIC", 0), RDS("RDS", 1), ECS("ECS", 2), VPC("VPC", 3);。
        :param addrOrigin: (Optional) 原生地址，RDS，DRDS为实例id。
        :param addrKey: (Optional) 保留字段。
        :param extra: (Optional) 保留字段。
        """

        self.id = id
        self.ip = ip
        self.port = port
        self.dbName = dbName
        self.modifiedBy = modifiedBy
        self.status = status
        self.userName = userName
        self.passwd = passwd
        self.passwdEcrypt = passwdEcrypt
        self.cdsCluster = cdsCluster
        self.dbType = dbType
        self.createTime = createTime
        self.environmentType = environmentType
        self.dbTypeName = dbTypeName
        self.sensitivity = sensitivity
        self.userType = userType
        self.mongoAuth = mongoAuth
        self.schemaCname = schemaCname
        self.schemaDepartment = schemaDepartment
        self.schemaDba = schemaDba
        self.schemaOwner = schemaOwner
        self.isStandard = isStandard
        self.coldict = coldict
        self.version = version
        self.schemaEnvironment = schemaEnvironment
        self.query = query
        self.region = region
        self.addrMode = addrMode
        self.addrOrigin = addrOrigin
        self.addrKey = addrKey
        self.extra = extra
