# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-11
Email  : belongmyth at 163.com
'''
from datetime import datetime

from sqlalchemy import Column, VARCHAR, DATE,DATETIME, Enum, ForeignKey,INTEGER
from sqlalchemy.orm import relationship, backref
from sqlalchemy.exc import IntegrityError

from base import BaseModel
from user import User
from const import EmployeeState, CompanyState,UserState
from util import generate_id


class Company(BaseModel):
    '''
       公司表
    '''
    __tablename__ = 'mc_company'

    id = Column('id', VARCHAR(40), primary_key=True)
    name = Column('name', VARCHAR(50), nullable=False)  # 公司名称
    addr = Column('addr', VARCHAR(100))  # 公司地址
    tel = Column('tel', VARCHAR(20))  # 公司电话
    owner_id = Column('owner_id', ForeignKey(User.id), nullable=True)  # 公司法人
    biller_id = Column('biller_id', ForeignKey(User.id), nullable=True)  # 公司账单联系人
    service_start = Column('service_start', DATE)  # 服务开始时间
    service_end = Column('service_end', DATE)  # 服务结束时间
    state = Column('state', Enum(*CompanyState.options), default=CompanyState.ACTIVE)  # 公司状态
    created = Column('created', DATETIME, default=datetime.now)

    owner = relationship(User, primaryjoin=owner_id == User.id,
                         backref=backref('company', uselist=False))  # ,foreign_keys=[owner_id]
    biller = relationship(User, primaryjoin=biller_id == User.id)  # ,foreign_keys=[biller_id]
    _employees = relationship('Employee', backref='company')  # 公司员工列表

    @property
    def employees(self):
        emps = []
        if self._employees is None:
            return emps
        for e in self._employees:
            if e.inservice:  #在职员工
                emps.append(e)
        return emps

    @classmethod
    def all(cls):
        '''
        公司列表接口，返回全部公司列表
        :return:全部公司列表
        '''
        return cls.objects.all()

    def save(self, commit=True):
        '''
        保存当前公司对象到数据库
        :param commit: 是否提交更改到数据库,默认True
        :return:
        '''
        while True:
            try:
                if self.id is None:
                    self.id = generate_id()
                    self.session.add(self)
                if commit:
                    self.session.commit()
                break
            except IntegrityError as e:  #
                self.logger.warn('found a duplicate company id %s'%self.id)
                self.session.rollback()
                self.id = None

    def json(self):
        data = {
            'id': self.id,
            'name': self.name,
            'addr': self.addr,
            'tel': self.tel,
            'owner_id':self.owner_id,
            # 'biller_id':self.biller_id,
            'owner': self.owner.json(with_apikey=False) if self.owner else None,
            #'billing': self.biller.json(with_apikey=False) if self.biller else None,
            'service_start': self.service_start.strftime('%Y-%m-%d') if self.service_start else None,
            'service_end': self.service_end.strftime('%Y-%m-%d') if self.service_end else None,
            'employees': [e.user.json(with_apikey=False) for e in self.employees]
        }
        return data

    def set_owner(self,owner_id):
        self.owner_id = owner_id
        self.save()
        self.addEmployee(owner_id)

    def set_biller(self,biller_id):
        self.biller_id = biller_id
        self.save()
        self.addEmployee(biller_id)

    def addEmployee(self, emp_id):
        exist = Employee.objects.filter(Employee.company_id==self.id).filter(Employee.employee_id==emp_id).first()
        if exist:
            exist.state = EmployeeState.ACTIVE
            exist.save()
        else:
            emp = Employee(company_id=self.id, employee_id=emp_id)
            self._employees.append(emp)
            self.session.commit()

    def delEmployee(self, emp_id):
        for e in self._employees:
            if e.employee_id == emp_id:
                e.state = EmployeeState.DELETE
                break
        self.session.commit()

    #
    # def addEmployee(self, emp_id, commit=True):
    #     for e in self.employees:
    #         if e.employee_id == emp_id:
    #             return
    #     emp = Employee(company_id=self.id, employee_id=emp_id)
    #     self._employees.append(emp)  # or self.session.add(emp)
    #     if commit:
    #         self.session.commit()
    #
    # def delEmployee(self, emp_id, commit=True):
    #     try:
    #         emp = Employee.objects.filter(Employee.employee_id == emp_id).first()
    #         if emp:
    #             emp.state = EmployeeState.DELETE
    #         if commit:
    #             self.session.commit()
    #     except ValueError as e:
    #         self.logger.error('when del employee %s, an error happend:%s' % (emp_id, e))

    @classmethod
    def testdata(cls):
        c = cls(name='MaiChuang')
        c.save()
        c.id = 'wc201408080000'
        c.save()

    @classmethod
    def testdata2(cls):
        u = User.objects.first()
        c = cls.objects.first()
        c.owner_id = u.id
        c.save()

    def __str__(self):
        return '<Company(%s,owner is %s,has %d employees)' % (self.name, self.owner.login_email, len(self.employees))

    def __repr__(self):
        return self.__str__()

class CompanyAlias(BaseModel):
    __tablename__ = 'mc_company_alias'

    id = Column('id',INTEGER,primary_key=True)
    alias = Column('alias',VARCHAR(20),nullable=False)
    company_id = Column('company_id',ForeignKey(Company.id))

    company = relationship(Company,backref = backref('alias',uselist = False))

    def save(self, commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

class Employee(BaseModel):
    '''
       公司员工表
    '''
    __tablename__ = 'mc_employee'
    company_id = Column('company_id', ForeignKey(Company.id), primary_key=True)
    employee_id = Column('employee_id', ForeignKey(User.id), primary_key=True)
    join_date = Column('join_date', DATETIME, default=datetime.now)
    state = Column('state', Enum(*EmployeeState.options), default=EmployeeState.ACTIVE)

    #company = relationship(Company)
    user = relationship(User)

    def __init__(self, company_id, employee_id):
        self.company_id = company_id
        self.employee_id = employee_id

    @property
    def inservice(self):
        return self.state == EmployeeState.ACTIVE and self.user.state == UserState.ACTIVE

    def save(self, commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def delete(self):
        self.state = EmployeeState.DELETE
        self.save()

    def __str__(self):
        return '<Employee(%s in %s)>' % (self.user.login_email, self.company.name)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def testdata3(cls):
        us = User.objects.all()
        cs = Company.objects.all()
        for i in range(0,len(us)):
            e = cls(company_id=cs.pop(0).id, employee_id=us.pop(0).id)
            e.save()