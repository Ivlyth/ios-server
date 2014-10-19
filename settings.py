# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-9
Email  : belongmyth at 163.com
'''

import os,re,urllib2,socket
import logging

from tornado.options import define, options, parse_command_line


_basedir = os.path.dirname(__file__)


def _(path, baseDir=_basedir):
    return os.path.join(baseDir, path)

# 默认日志文件
_default_log_file = _('account_sys.log', _('logs'))

define('port', default=8888, type=int, help=u'Tornado will provide service on the given port')
define('initdb', default=False, type=bool, help=u'try to init database when tornado start')
define('initdata', default=False, type=bool, help=u'try to init table data when tornado start')
define('testdata', default=False, type=bool, help=u'insert some test data into database for test when tornado start')
define('onlyinit', default=False, type=bool, help=u'only init database , and will not start server')
define('debug', default=False, type=bool, help=u'run on the debug mode')
define('loglevel', default=logging.getLevelName(logging.INFO), type=str, help=u'Log Level')
define('logfile', default=_default_log_file, type=str, help=u'Log File')

parse_command_line()

_LOCAL = 1
_DEV = 2
_QA = 3
_PRODUCT = 4

RUNTIME_ENV = 4

def _env_check():
    try:
        local_ip = re.search('\d+\.\d+\.\d+\.\d+',urllib2.urlopen("http://www.whereismyip.com").read()).group(0)
        if local_ip == '115.182.75.8' and RUNTIME_ENV!=4:
            return False
        hostname = socket.gethostname()
        if hostname == 'localhost.localdomain' and local_ip == '101.231.200.10' and RUNTIME_ENV not in (2,3):
            return False
        if hostname != 'localhost.localdomain' and local_ip == '101.231.200.10' and RUNTIME_ENV != 1:
            return False
    except Exception as e:
        return False
    return True

#assert _env_check(),u'运行环境设置与当前设置不匹配请检查'

_mcaccount_mysqldb_host = 'localhost'
# 数据库配置
_db_config = {
    'db_type': 'mysql',
    'db_driven': 'mysqldb',
    'db_user': 'root',
    'db_passwd': 'bmw12345',
    'db_host': _mcaccount_mysqldb_host,#localhost
    'db_port': '3306',
    'db_selected_db': 'mcaccount',
    'db_charset': 'utf8'
}

_db_connect_params = '%(db_type)s+%(db_driven)s://%(db_user)s:%(db_passwd)s@%(db_host)s/%(db_selected_db)s?charset=%(db_charset)s'

# 数据库连接串，供sqlalchemy使用
DB_CONNECT_PARAMS = _db_connect_params % _db_config
DB_TIMEOUT = 3600

# FOR REDIS
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
#Tan14-Api默认过期时间为 2 小时
TAN14KEY_EXPIRE_SECONDS = 2 * 60 * 60

# FOR MONGO
MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_ACCESS_LOG_DB = 'mcaccount_access'
MONGO_ACCESS_LOG_COLLECTION = 'accesslogs'

BILLING_DB = 'mcaccount_billing'
LOGIN_HIS_DB = 'mcaccount_loginhis'

MONGO_USEFUL_LOG_DB = 'mcaccount_useful'

# log file for AccountServer
assert os.path.isdir(os.path.dirname(options.logfile)), '%s is not a valid directory' % os.path.dirname(options.logfile)
LOG_FILE = options.logfile

# it could be:
# DEBUG
# INFO
#   WARN
#   ERROR
#   FATAL
# Default is INFO(define in top)
LOG_LEVEL = options.loglevel.upper() if options.loglevel.upper() in (
'DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL') else logging.INFO

server_settings = {
    'debug': options.debug
}

# email settings
EMAIL_HOST = 'smtp.exmail.qq.com'
EMAIL_PORT = 25
EMAIL_USER = 'noreply@tan14.cn'
EMAIL_PASS = 'bmw12345'

# TAN14 CONSOLE HOST
TAN14_APP_ADDR = 'https://app.tan14.cn/#'
