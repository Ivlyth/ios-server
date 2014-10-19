#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-9-17
Email  : belongmyth at 163.com
'''

from datetime import datetime, timedelta

from sqlalchemy import Column, INTEGER, VARCHAR, DATETIME, BOOLEAN, ForeignKey, Enum, TEXT
from sqlalchemy.orm import relationship,backref

from base import BaseModel
from company import Company
from boss_models import BossChannel
from watermelong_models import WatermelonChannel
from const import ProductState, ProductInsState
from log.mongo import get_useful_col

_pnjson_col = get_useful_col('pnlist_json')

class Product(BaseModel):
    __tablename__ = 'mc_product'

    id = Column('id', INTEGER, primary_key=True) # 产品名称
    name = Column('name',VARCHAR(50), nullable=False) # 产品名称
    # alias = Column('alias',VARCHAR(50), nullable=False) # 产品别称 主要用在产品间 url 转发
    desc = Column('desc',VARCHAR(200), nullable= True)
    created = Column('created',DATETIME,default=datetime.now) # 产品创建时间
    state = Column('state', Enum(*ProductState.options), default=ProductState.ACTIVE) # 产品状态

    def save(self, commit = True):
        self.session.add(self)
        if commit:
            self.session.commit()

class ProductIns(BaseModel):
    __tablename__ = 'mc_product_ins'

    id = Column('id',VARCHAR(40),primary_key=True)# primary key ID
    desc = Column('desc',VARCHAR(200), nullable= True)
    product_id = Column('product_id',ForeignKey(Product.id)) # 产品ID
    company_id = Column('company_id',ForeignKey(Company.id)) # 公司ID
    created = Column('created',DATETIME,default=datetime.now) # 创建时间
    state = Column('state', Enum(*ProductInsState.options), default=ProductInsState.ACTIVE) # 产品使用状态

    product = relationship(Product)
    company = relationship(Company, backref = backref('products'))

    def save(self, commit = True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def channels(self):
        if self.product_id == 1:
            return BossChannel.objects.filter(BossChannel.pn == self.id).all()
        if self.product_id == 2:
            return WatermelonChannel.objects.filter(WatermelonChannel.pn == self.id).all()
        return []

    def _update(self):

        data = {
            'pn':self.id,
            'company':self.company.name,
            'company_alias':self.company.alias.alias if self.company.alias else None,
            'channels':[c.json() for c in self.channels()],
            'owner':self.company.owner.json(),
            'employees':[ e.user.json() for e in self.company.employees ],
            'website':[w.json() for w in self.product.websites ] if self.product.websites else None,
            'product_type':self.product.name
        }
        r = _pnjson_col.find_one({'pn':self.id})
        if r is None:
            _pnjson_col.insert({
                'pn':self.id,
                'data':data,
                'last_update':datetime.now()
            })
        else:
            _pnjson_col.update({'pn':self.id},{'$set':{
                'data':data,
                'last_update':datetime.now()
            }})

        return data

    def pn_json(self, force = False):
        json = _pnjson_col.find_one({'pn':self.id})

        if json is None or force:
            data = self._update()
        else:
            data = json['data']
            diff = datetime.now() - json['last_update']
            if diff.total_seconds() > 12*60*60: # half day
                data = self._update()

        return data

class WebSite(BaseModel):
    __tablename__ = 'mc_website'

    id = Column('id',INTEGER,primary_key= True)
    name = Column('name',VARCHAR(50),nullable= False)
    addr = Column('addr',VARCHAR(100))
    api_prefix = Column('api_prefix',VARCHAR(100))
    desc = Column('desc',VARCHAR(200),nullable=True)
    created = Column('created',DATETIME,default=datetime.now)
    product_id = Column('product_id',ForeignKey(Product.id)) # 网站对应产品 many to one

    product = relationship(Product , backref=backref('websites'))

    def save(self, commit = True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def json(self):
        data = {
            'id':self.id,
            'name':self.name,
            'desc':self.desc,
            'addr':self.addr,
            'api_prefix':self.api_prefix
        }
        return data

def getPN(app_name,company_id):
    website = WebSite.objects.filter(WebSite.name == app_name).first()
    if website is None:
        return None
    product_id = website.product_id
    product_ins = ProductIns.objects.filter(ProductIns.company_id == company_id)\
        .filter(ProductIns.product_id == product_id)\
        .filter(ProductIns.state == ProductInsState.ACTIVE).first()
    if product_ins is None:
        return None
    return product_ins.id