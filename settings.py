# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-9
Email  : belongmyth at 163.com
'''

import os
import logging

from tornado.options import define, options, parse_command_line


_basedir = os.path.dirname(__file__)

def _(path, baseDir=_basedir):
    return os.path.join(baseDir, path)

define('port', default=8888, type=int, help=u'Tornado will provide service on the given port')
define('initdb', default=False, type=bool, help=u'try to init database when tornado start')
define('initdata', default=False, type=bool, help=u'try to init table data when tornado start')
define('testdata', default=False, type=bool, help=u'insert some test data into database for test when tornado start')
define('onlyinit', default=False, type=bool, help=u'only init database , and will not start server')
define('debug', default=False, type=bool, help=u'run on the debug mode')
define('loglevel', default=logging.getLevelName(logging.INFO), type=str, help=u'Log Level')


parse_command_line()

# 数据库配置
_db_config = {
    'db_type': 'mysql',
    'db_driven': 'mysqldb',
    'db_user': 'root',
    'db_passwd': 'bmw12345',
    'db_host': 'localhost',
    'db_port': '3306',
    'db_selected_db': 'iosserver',
    'db_charset': 'utf8'
}

_db_connect_params = '%(db_type)s+%(db_driven)s://%(db_user)s:%(db_passwd)s@%(db_host)s/%(db_selected_db)s?charset=%(db_charset)s'

TABLE_PREFIX = 'ios_'

# 数据库连接串，供sqlalchemy使用
DB_CONNECT_PARAMS = _db_connect_params % _db_config
DB_TIMEOUT = 3600

server_settings = {
    'debug': options.debug
}
