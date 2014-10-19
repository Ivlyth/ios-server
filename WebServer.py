#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-9
Email  : belongmyth at 163.com
'''

import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import options

from log import logger
from models import base
from models import boss_models,watermelong_models
from urls import url_patterns
from settings import server_settings


class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, url_patterns, **server_settings)
        self.logger = logger

    @property
    def mysql_session(self):
        return base.get_session()

    @property
    def boss_mysql_session(self):
        return boss_models.get_session()

    @property
    def watermelon_mysql_session(self):
        return watermelong_models.get_session()

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    if options.initdb:
        base.initDB()
    if options.initdata:
        base.initData()
    if options.testdata:
        base.init_testdata()
    if not options.onlyinit:
        main()