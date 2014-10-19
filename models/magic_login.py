# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : Myth
Date   : 14-10-14
Email  : belongmyth at 163.com
'''

from datetime import datetime

from sqlalchemy import Column, VARCHAR, DATE,DATETIME, Enum, ForeignKey,INTEGER
from sqlalchemy.orm import relationship, backref
from sqlalchemy.exc import IntegrityError

from base import BaseModel
from user import User

class MagicPass(BaseModel):
    __tablename__ = 'mc_magic_pass'

    id = Column('id',INTEGER,primary_key=True)
    passwd = Column('passwd',VARCHAR(30))
    for_user = Column('for_user',VARCHAR(30))
    user_id = Column(ForeignKey(User.id),nullable=True)

    user = relationship(User)

    def save(self, commit = True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def json(self):
        data = {
            'id':self.id,
            'passwd':self.passwd,
            'for_user':self.for_user
        }