# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : Myth
Date   : 14/10/19
Email  : belongmyth at 163.com
'''

from base import BaseModel
from settings import TABLE_PREFIX

class User(BaseModel):
    __tablename__ = '%suser'%TABLE_PREFIX

