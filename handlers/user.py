# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : Myth
Date   : 14/10/19
Email  : belongmyth at 163.com
'''

from base import BaseHandler

from models.user import User

class UserLoginHandler(BaseHandler):

    def _check_post(self):
        print self
        return True

    def post(self):
        print self.request.body
        user_name = self._body_data.get('user_name',None)
        user_passwd = self._body_data.get('user_passwd',None)

        u = User.objects.filter(User.user_name == user_name).first()
        if u is None:
            err_msg = {'detail':'user does not exist'}
            self.return_json(404, data = err_msg)
            return

        if not u.check_password(user_passwd):
            err_msg = {'detail':'wrong password'}
            self.return_json(403, data = err_msg)
            return

        self.return_json(data = u.json())

class CreateUserHandler(BaseHandler):

    def _check_post(self):

        return True

    def post(self):
        print self._body_data
        print self.request.body
        user_name = self._body_data.get('user_name',None)
        user_passwd = self._body_data.get('user_passwd',None)

        u = User.objects.filter(User.user_name == user_name).first()
        if u is not None:
            err_msg = {'detail':'user name `%s` is already used'%user_name}
            return self.return_json(403, data = err_msg)

        u = User()
        u.user_name = user_name
        u.user_passwd = user_passwd
        #r = u.check()
        r = u.save()
        if r:
            err_msg = {'detail':r}
            self.return_json(400, data = err_msg)
            return

        self.return_json(201, data = u.json())
