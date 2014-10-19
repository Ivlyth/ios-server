# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-12
Email  : belongmyth at 163.com
'''

from datetime import datetime

from sqlalchemy import Column, INTEGER, VARCHAR, DATETIME, ForeignKey
from sqlalchemy.orm import relationship

from base import BaseModel
from api import API
from const import Roles
from util import check_permission, get_permission


class Role(BaseModel):
    __tablename__ = 'mc_role'

    id = Column('id', VARCHAR(30), primary_key=True)
    name = Column('name', VARCHAR(30), unique=True, nullable=False)
    desc = Column('desc', VARCHAR(100))
    created = Column('created', DATETIME, default=datetime.now)

    users = relationship('User')
    permissions = relationship('Permission')

    def __str__(self):
        return '<Role(%s,%d users)>' % (self.name, len(self.users))

    def __repr__(self):
        return self.__str__()

    def save(self, commit = True):
        self.session.add(self)
        if commit:
            self.session.commit()

    @classmethod
    def init_table(cls):
        for name,desc in Roles.CHOICES:
            role = cls(id=name,name=name,desc=desc)
            cls.session.add(role)
        cls.session.commit()

    def json(self, with_permissions = False):
        data = {
            'id': self.id,
            'name': self.name,
            'desc': self.desc
        }
        if with_permissions:
            data['ps'] = [p.json() for p in self.permissions]
        return data

    @classmethod
    def roles(cls):
        rs = []
        for r in cls.objects.filter(Role.name!=Roles.MAICHUANG).filter(Role.name!=Roles.OWNER).all():
            rs.append(r.json())
        return rs


class Permission(BaseModel):
    __tablename__ = 'mc_role_permission'

    id = Column('id', INTEGER, primary_key=True)
    role_id = Column('role_id', ForeignKey(Role.id), nullable=False)
    api_id = Column('api_id', ForeignKey(API.id), nullable=False)
    permission = Column('permission', INTEGER, nullable=False)

    role = relationship(Role)
    api = relationship(API)

    def save(self, commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def __str__(self):
        return '<Perssion(%s-%s)>' % (self.api.handler, get_permission(self.permission))

    def __repr__(self):
        return self.__str__()

    def check(self, method):
        return check_permission(self.permission, method)

    @property
    def GET(self):
        return self.check('GET')

    @property
    def POST(self):
        return self.check('POST')

    @property
    def PUT(self):
        return self.check('PUT')

    @property
    def DELETE(self):
        return self.check('DELETE')

    @property
    def HEAD(self):
        return self.check('HEAD')

    @property
    def OPTIONS(self):
        return self.check('OPTIONS')

    def json(self):
        data = {
            'id':self.id,
            'api':self.api.json(),
            'GET':self.GET,
            'PUT':self.PUT,
            'POST':self.POST,
            'HEAD':self.HEAD,
            'DELETE':self.DELETE,
            'OPTIONS':self.OPTIONS
        }
        return data

    @classmethod
    def testdata3(cls):
        import random

        roles = Role.objects.all()
        apis = API.objects.all()
        for role in roles:
            for api in apis:
                p = cls(role_id=role.id, api_id=api.id, permission=random.randint(0, 63))
                cls.session.add(p)
        cls.session.commit()
