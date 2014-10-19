#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-30
Email  : belongmyth at 163.com
'''
from datetime import datetime
from log.mongo import get_billing_detail
from base import BaseModel
from models.const import CDNServices
from company import Company
from sqlalchemy import Column, INTEGER, VARCHAR, DATETIME, ForeignKey,DECIMAL,BOOLEAN,NUMERIC,TEXT
from sqlalchemy.orm import relationship,backref
import json

class CDNServiceType(BaseModel):
    '''
       服务类型
    '''
    __tablename__ = 'mc_service_type'

    id = Column('id',INTEGER,primary_key=True)
    name = Column('name',VARCHAR(20)) #服务收费类型名称
    verbose_name = Column('verbose_name',VARCHAR(50))#服务收费名称
    desc = Column('desc', VARCHAR(200))#收费描述
    unit_price = Column('unit_price',NUMERIC(18,3),default=1) #单价
    is_graduated = Column('is_graduated',BOOLEAN,default=False)#是否阶梯计费
    graduated_config = Column('graduated_config',VARCHAR(2000))#阶梯配置
    created = Column('created', DATETIME, default=datetime.now)

    def save(self, commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

    @classmethod
    def init_table(cls):
        for NAME,VERBOSE_NAME, DESC, IS_GRADUATED, GRADUATED_CONFIG in CDNServices.CHOICES:
            st = cls()
            st.name = NAME
            st.verbose_name = VERBOSE_NAME
            st.desc=DESC
            st.is_graduated = IS_GRADUATED
            st.graduated_config = json.dumps(GRADUATED_CONFIG) if GRADUATED_CONFIG else None
            st.save()

class BillConfig(BaseModel):
    '''
       公司账单配置
    '''
    __tablename__ = 'mc_billconfig'

    id = Column('id', INTEGER, primary_key=True)
    company_id = Column('company_id', ForeignKey(Company.id), nullable=False) #公司ID
    service_type_id = Column('service_type_id',ForeignKey(CDNServiceType.id),nullable=False) #服务计费类型
    unit_price = Column('unit_price',NUMERIC(18,3)) #单价
    real_ratio = Column('real_ratio',NUMERIC(4,2),default=1.00) #折扣系数
    last_update = Column('last_update',DATETIME,default=datetime.now) #最后更新配置时间

    company = relationship(Company,backref = backref('billconfig',uselist=False))
    cdnservice = relationship(CDNServiceType)

    def save(self, commit=True):
        self.last_update = datetime.now()
        self.session.add(self)
        if commit:
            self.session.commit()

    @classmethod
    def testdata2(cls):
        c = Company.objects.first()
        s = CDNServiceType.objects.filter(CDNServiceType.name==CDNServices.T_FZ).first()
        bc = cls(company_id = c.id,service_type_id=s.id,unit_price=23.45)
        bc.save()

class Bill(BaseModel):
    '''
       公司账单
    '''
    __tablename__ = 'mc_bill'

    id = Column('id',INTEGER,primary_key=True)
    company_id = Column('company_id',ForeignKey(Company.id))
    bill_date = Column('bill_date',VARCHAR(10))#yyyymm
    service_type = Column('service_type',VARCHAR(20)) # value of CDNServiceType.name
    service_name = Column('service_name',VARCHAR(50)) # value of CDNServiceType.verbose_name
    service_desc = Column('service_desc',VARCHAR(200)) # value of CDNServiceType.desc
    #unit_price = Column('unit_price',NUMERIC(18,3)) #单价
    total_use = Column('total_use',NUMERIC(18,2)) #使用的总流量或者带宽数量
    max_use = Column('max_use',NUMERIC(18,2)) #最大的流量或者带宽数量
    real_ratio = Column('real_ratio',DECIMAL(3,2)) #折扣系数 value of BillConfig.real_ratio
    total_price = Column('total_price',DECIMAL(18,2))#账单总价
    total_ratio_price = Column('total_ratio_price',DECIMAL(18,2))#账单打折后总价
    created = Column('created',DATETIME,default=datetime.now)#账单生成时间
    is_invoice = Column('is_invoice',BOOLEAN,default=False)#是否已经开发票
    is_pay = Column('is_pay',BOOLEAN,default=False)#是否已经付款
    bill_data = Column('bill_data',TEXT)
    detail = Column('detail',VARCHAR(100))#MONGODB KEY
    month_detail = Column('month_detail',VARCHAR(100))#MONGODB KEY

    def save(self, commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def detail_data(self):
        return get_billing_detail(self.company_id,self.detail)

    def month_detail_data(self):
        return get_billing_detail(self.company_id,self.month_detail)

    def json(self):
        data={
            'service_name':self.service_name,
            'service_desc':self.service_desc,
            'bill_date':self.bill_date,
            'real_ratio':float(self.real_ratio),
            'max_use':float(self.max_use),
            'total_use':float(self.total_use),
            'total_price':float(self.total_price),
            'total_ratio_price':float(self.total_ratio_price),
            'is_invoice':self.is_invoice,
            'is_pay':self.is_pay,
            'detail':self.detail_data(),
            'month_detail':self.month_detail_data(),
            'bill_data': self.bill_data
        }
        return data