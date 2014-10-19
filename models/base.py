#!/usr/bin/evn python
# -*- coding:utf-8 -*-
'''
Author : myth
Date   : 14-7-9
Email  : belongmyth at 163.com
'''

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from settings import DB_CONNECT_PARAMS


#DB_CONNECT_PARAMS='mysql+mysqldb://root:root@localhost/account?charset=utf8'
engine = create_engine(DB_CONNECT_PARAMS, echo=False, pool_recycle=5)  # TODO

maker = sessionmaker(bind=engine)
DBSession = scoped_session(maker)

BaseModel = declarative_base(bind=engine)

BaseModel.session = DBSession  # all model will have it
BaseModel.objects = DBSession.query_property()  # all model will have it
BaseModel.__table_args__ = {  # 指定所有model的默认参数
                              'mysql_charset': 'utf8',
                              'mysql_engine': 'InnoDB'
}


def change_session(session):
    global BaseModel, DBSession
    BaseModel.session = session
    DBSession = session


def get_session():
    global DBSession
    return DBSession


# def change_engine(engine):
# global BaseModel, DBSession
#     DBSession.configure(bind=engine)
#     BaseModel.session = DBSession


def init_db():
    BaseModel.metadata.create_all(engine)


def drop_db():
    BaseModel.metadata.drop_all(engine)


def initDB():
    init_db()

if __name__ == '__main__':
    init_db()

