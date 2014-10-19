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

from models import base
from urls import url_patterns
from settings import server_settings


class Application(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, url_patterns, **server_settings)

    @property
    def mysql_session(self):
        return base.get_session()

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    if options.initdb:
        base.initDB()
    if not options.onlyinit:
        main()