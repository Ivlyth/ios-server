#!/usr/bin/evn python
# -*- coding:utf-8 -*-
'''
Author : myth
Date   : 14-10-03
Email  : belongmyth at 163.com
'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import Column, ForeignKey, String, Integer
from sqlalchemy.orm import relationship, backref
from settings import BOSS_DB_CONNECT_PARAMS

engine = create_engine(BOSS_DB_CONNECT_PARAMS, echo=False, pool_recycle=5)  # TODO

maker = sessionmaker(bind=engine)
DBSession = scoped_session(maker)

def get_session():
    global DBSession
    return DBSession

BaseModel = declarative_base(bind=engine)

BaseModel.session = DBSession  # all model will have it
BaseModel.objects = DBSession.query_property()  # all model will have it
BaseModel.__table_args__ = {  # 指定所有model的默认参数
                              'mysql_charset': 'utf8',
                              'mysql_engine': 'InnoDB'
}


class BossChannel(BaseModel):
    __tablename__ = 'channels'

    # 自增
    id = Column(String(56), primary_key=True, unique=True)
    # 产品编号
    pn = Column(String(56), index=True)
    remark = Column(String(1024), nullable=False)
    online = Column(Integer, nullable=False, default=1)  # 状态：开启/关闭
    applied = Column(Integer, nullable=False, default=0)  # 状态：激活/非激活 1 / 0

    def json(self):
        data = {
            'channel_id':self.id,
            'remark':self.remark,
            'online':True if self.online else False,
            'applied':True if self.applied else False,
            'domains':[d.json() for d in self.domains]
        }
        return data

    def save(self):
        self.session.add(self)
        self.session.commit()


class BossDomain(BaseModel):
    __tablename__ = 'domains'

    id = Column(Integer, primary_key=True)
    #channel_id = Column(String(56))
    channel_id = Column(ForeignKey(BossChannel.id))
    domain = Column(String(255), nullable=False, unique=True)
    pingback = Column(String(1024), nullable=False)
    icp = Column(String(255))
    ssl = Column(Integer, default=0)
    dnspod_id = Column(Integer)  # DNSPOD id
    remark = Column(String(1024))
    cname = Column(String(50))  #cname

    channel = relationship(BossChannel,backref = backref('domains'))

    def save(self):
        self.session.add(self)
        self.session.commit()

    def json(self):
        data = {
            'domain':self.domain,
            'pingback':self.pingback,
            'ssl':self.ssl,
            'remark':self.remark,
            'cname':self.cname
        }
        return data