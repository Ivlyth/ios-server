# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : Myth
Date   : 14/10/19
Email  : belongmyth at 163.com
'''

from base import BaseModel,TABLE_NAME
from datetime import datetime

from sqlalchemy import Column, VARCHAR,INTEGER,DATETIME
from sqlalchemy.orm import relationship, backref
from sqlalchemy.exc import IntegrityError


class User(BaseModel):
    __tablename__ = TABLE_NAME('user')

    id = Column('id',INTEGER,primary_key= True) # user id  , auto inc
    user_name = Column('user_name',VARCHAR(50),nullable= False)
    user_passwd = Column('user_passwd',VARCHAR(30), nullable=False)
    nick_name = Column('nick_name',VARCHAR(30))# not use for now
    tel = Column('tel',VARCHAR(30))
    created = Column('created',DATETIME,default =datetime.now)

    def _check_for_user_name(self):
        # if check failed, return a reason, None for success
        if len(self.user_name) > 50:
            return 'length of user name must be less than 50 chars'
        return None

    def _check_for_user_passwd(self):

        return None

    def _check_for_nick_name(self):

        return None

    def _check_for_tel(self):

        return None

    # for json out put
    def json(self):
        data = {
            'id':self.id,
            'user_name':self.user_name,
            'nick_name':self.nick_name,
            'tel':self.tel
        }
        return data

    #
    def check_password(self, passwd):

        return True

