#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-9-29
Email  : belongmyth at 163.com
'''

from datetime import datetime

from sqlalchemy import Column, INTEGER, VARCHAR, DATETIME, ForeignKey
from sqlalchemy.orm import relationship,backref

from base import BaseModel
from company import Company

class Agent(BaseModel):
    __tablename__ = 'mc_agent'

    id = Column('id',INTEGER,primary_key=True)
    name = Column('name',VARCHAR(30)) #代理商名称
    alias = Column('alias',VARCHAR(30)) #代理商别称
    tel = Column('tel',VARCHAR(30)) #代理商联系电话
    created = Column('created',DATETIME,default=datetime.now)

    #companys

    def save(self, commit = True):
        self.session.add(self)
        if commit:
            self.session.commit()

class AgentCompanyMap(BaseModel):
    __tablename__ = 'mc_agent_map'

    id = Column('id', INTEGER, primary_key= True)
    agent_id = Column(ForeignKey(Agent.id),nullable=False)
    company_id = Column(ForeignKey(Company.id),nullable=False)
    created = Column('created',DATETIME,default=datetime.now)

    agent = relationship(Agent,backref = backref('companys'))
    company = relationship(Company,backref = backref('agent',uselist=False))

    def save(self, commit = True):
        self.session.add(self)
        if commit:
            self.session.commit()