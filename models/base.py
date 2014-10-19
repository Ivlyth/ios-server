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

import models
from util import md5_value
from settings import DB_CONNECT_PARAMS


#DB_CONNECT_PARAMS='mysql+mysqldb://root:root@localhost/account?charset=utf8'
engine = create_engine(DB_CONNECT_PARAMS, echo=False, pool_recycle=5)  # TODO

maker = sessionmaker(bind=engine)
DBSession = scoped_session(maker)

BaseModel = declarative_base(bind=engine)

BaseModel.session = DBSession  # all model will have it
BaseModel.objects = DBSession.query_property()  # all model will have it
BaseModel.logger = logger
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

def create_maichuang_test():
    users = []
    c = models.Company(id = md5_value('wc201307150000')[8:30] , name=u'上海脉创有限公司测试')#
    models.Company.session.add(c)
    models.Company.session.commit()
    b = models.BillConfig()
    b.company_id = c.id
    b.service_type_id = 1
    b.unit_price = 1.0
    b.real_ratio = 1.0
    b.save()
    #Admin Owner
    u = models.User(nickname='Admin',login_email='admin@maichuang.net',login_passwd='maichuang',role_id='Owner')
    users.append(u)#u.save()
    c.owner_id = u.id
    #Root
    u = models.User(nickname='Root',login_email='root@maichuang.net',login_passwd='maichuang',role_id='Root')
    users.append(u)#u.save()
    #seven
    u = models.User(nickname='Seven',login_email='seven.chen@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    u = models.User(nickname='Humen',login_email='humen1@gmail.com',login_passwd='123123',role_id='Root')
    users.append(u)#u.save()
    #myth
    u = models.User(nickname='Myth',login_email='myth.ren@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #daemon
    u = models.User(nickname='Daemon',login_email='daemon.xie@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #luck
    u = models.User(nickname='Luck',login_email='luck.li@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #Luffy
    u = models.User(nickname='Luffy',login_email='luffy.liu@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #saive
    u = models.User(nickname='Saive',login_email='saive.jiang@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #dennis
    u = models.User(nickname='Dennis',login_email='dennis.zhao@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #michael
    u = models.User(nickname='Michael',login_email='michael.huang@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #Derrick
    u = models.User(nickname='Derrick',login_email='derrick.jiang@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #kanon
    u = models.User(nickname='kanon',login_email='kanon.zhou@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #Kent
    u = models.User(nickname='Kent',login_email='kent.zhou@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #Kevin
    u = models.User(nickname='Kevin',login_email='kevin.liu@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #Macor
    u = models.User(nickname='Macor',login_email='macor.dai@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #XiaoWei
    u = models.User(nickname='XiaoWei',login_email='xiaowei.wang@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #Jessie
    u = models.User(nickname='Jessie',login_email='jessie.zhang@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #Frain
    u = models.User(nickname='Frain',login_email='frain.zhang@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #Juno
    u = models.User(nickname='Juno',login_email='juno.zhu@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #YiJun
    u = models.User(nickname='YiJun',login_email='yijun.liu@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    #FengHao
    u = models.User(nickname='FengHao',login_email='hao.feng@maichuang.net',login_passwd='maichuang',role_id='SuperUser')
    users.append(u)#u.save()
    for u in users:
        u.save()
        u.create_apikey()
        c.addEmployee(u.id)

def init_users():
    '''
       系统初始化公司 与 用户
    '''
    c = models.Company(name=u'上海脉创网络科技有限公司')#
    c.save()
    b = models.BillConfig()
    b.company_id = c.id
    b.service_type_id = 1
    b.unit_price = 1
    b.real_ratio = 1
    b.save()
    #Root
    u = models.User(nickname='Root',login_email='root@tan14.cn',login_passwd='tan14.cn',role_id='Root')
    u.save()
    c.owner_id = u.id
    c.addEmployee(u.id)
    #Admin Owner
    u = models.User(nickname='Admin',login_email='admin@tan14.cn',login_passwd='tan14.cn',role_id='Owner')
    u.save()
    c.addEmployee(u.id)

def init_permission():
    from permission_tool import permission_import
    # ok

def initDB():
    init_db()

def initData():
    for attr in dir(models):
        model = getattr(models, attr, None)
        if hasattr(model, 'init_table'):
            if issubclass(model, BaseModel):
                model.init_table()
    init_users()
    create_maichuang_test()
    init_permission()

def init_testdata():
    pass
    # 创建测试用户
    # for attr in dir(models):
    #     model = getattr(models, attr, None)
    #     if hasattr(model, 'testdata'):
    #         if issubclass(model, BaseModel):
    #             model.testdata()
    #
    # for attr in dir(models):
    #     model = getattr(models, attr, None)
    #     if hasattr(model, 'testdata2'):
    #         if issubclass(model, BaseModel):
    #             model.testdata2()
    #
    # for attr in dir(models):
    #     model = getattr(models, attr, None)
    #     if hasattr(model, 'testdata3'):
    #         if issubclass(model, BaseModel):
    #             model.testdata3()


if __name__ == '__main__':
    init_db()

