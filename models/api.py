# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-11
Email  : belongmyth at 163.com
'''

from datetime import datetime

from sqlalchemy import Column, INTEGER, VARCHAR, DATETIME, ForeignKey
from sqlalchemy.orm import relationship

from base import BaseModel
from const import Services


class Service(BaseModel):
    __tablename__ = 'mc_service'

    id = Column('id', INTEGER, primary_key=True)
    name = Column('name', VARCHAR(30))
    desc = Column('desc', VARCHAR(200))
    created = Column('created', DATETIME, default=datetime.now)

    def __str__(self):
        return '<Service(%s)>' % self.name

    def __repr__(self):
        return self.__str__()

    def save(self,commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def json(self):
        data = {
            'id':self.id,
            'name':self.name,
            'desc':self.desc
        }
        return data

    @classmethod
    def init_table(cls):
        for name in Services.CHOICES:
            service = cls(name=name)
            cls.session.add(service)
        cls.session.commit()


class API(BaseModel):
    __tablename__ = 'mc_apilist'

    id = Column('id', INTEGER, primary_key=True)
    service_id = Column('service_id', ForeignKey(Service.id), nullable=False)
    handler = Column('handler', VARCHAR(50), nullable=False)
    desc = Column('desc', VARCHAR(200))
    created = Column('created', DATETIME, default=datetime.now)

    service = relationship(Service)

    def save(self,commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

    @property
    def service_name(self):
        return self.service.name

    def __str__(self):
        return '<API(service is %s , handler is %s)>' % (self.service_name, self.handler)

    def __repr__(self):
        return self.__str__()

    def json(self):
        data = {
            'id':self.id,
            'handler':self.handler,
            'desc':self.desc,
            'service':self.service.json()
        }
        return data

    @classmethod
    def testdata2(cls):
        handlers = []
        import random, string

        string.lowercase
        services = Service.objects.all()
        for s in services:
            for i in range(10):
                while True:
                    h = ''.join([random.choice(string.lowercase) for i in range(8)])
                    if h not in handlers:
                        break
                a = cls(service_id=s.id, handler=h)
                cls.session.add(a)
        cls.session.commit()
