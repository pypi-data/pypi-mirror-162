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


class DbcmColumn(object):

    def __init__(self, old_column_name=None, column_name=None, column_type=None, column_length=None, column_point=None, is_null=None, column_value=None, auto_incre=None, pk_index=None, column_comments=None):
        """
        :param old_column_name: (Optional) 原始列表。
        :param column_name: (Optional) 列名。
        :param column_type: (Optional) 列类型。
        :param column_length: (Optional) 列长度。
        :param column_point: (Optional) 小数点后长度。
        :param is_null: (Optional) 是否可以为空。
        :param column_value: (Optional) 列默认值。
        :param auto_incre: (Optional) 是否自增。
        :param pk_index: (Optional) 是否为主键。
        :param column_comments: (Optional) 列注释。
        """

        self.old_column_name = old_column_name
        self.column_name = column_name
        self.column_type = column_type
        self.column_length = column_length
        self.column_point = column_point
        self.is_null = is_null
        self.column_value = column_value
        self.auto_incre = auto_incre
        self.pk_index = pk_index
        self.column_comments = column_comments
