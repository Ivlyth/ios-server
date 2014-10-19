#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-9
Email  : belongmyth at 163.com
'''
from handlers.user import UserLoginHandler,CreateUserHandler

root_url = ''  #'/account'

url_patterns = [
    # TEST
    (r'^%s/user/login/?$' % root_url, UserLoginHandler),
    (r'^%s/user/create/?$' % root_url, CreateUserHandler)
]