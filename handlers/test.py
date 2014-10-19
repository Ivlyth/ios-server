#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-16
Email  : belongmyth at 163.com
'''

from base import BaseHandler
from decorators.auth import auth
from models.user import LoginHis

#@auth
class testHandler(BaseHandler):

    def get(self):
        print self.get_request_data()
        self.write('Hello , your request method is ' + self.request.method)
        self.write('<br/>')
        self.write('url path is %s'%self.request.path)

    def post(self):
        self.get_request_data()
        self.write('Hello , your request method is ' + self.request.method)

    def head(self):
        self.write('Hello , your request method is ' + self.request.method)

    def put(self):
        self.write('Hello , your request method is ' + self.request.method)

    def delete(self):
        self.write('Hello , your request method is ' + self.request.method)

    def options(self):
        self.write('Hello , your request method is ' + self.request.method)


class testHandler2(BaseHandler):

    def prepare(self):
        print self.SUPPORTED_METHODS

    def get(self):
        from datetime import datetime as datetime

        print 'I am test2,i am here', datetime.now()


class LoginHisHandler(BaseHandler):

    def get(self):
        his = LoginHis.objects.all()
        result = []
        for h in his:
            result.append(h.json())
        return self.return_json(data=result)