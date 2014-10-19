#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-8-5
Email  : belongmyth at 163.com
'''

from base import BaseHandler
from util import get_bill_date
from handlers.company import BaseCompanyHandler
from models.bill import Bill
from models.company import Company
from decorators.auth import auth

@auth
class BillHandler(BaseCompanyHandler):


    def get(self,company_id, bill_date):

        company = Company.objects.filter(Company.id == company_id).first()

        #TODO for test , uncomment the next two line for production
        if not self.check_relation_company(company):
           return

        if bill_date is None:
            bill_date = get_bill_date()
        b = Bill.objects.filter(Bill.company_id==company_id).filter(Bill.bill_date == bill_date).first()
        if not b:
            err_msg = {'detail':'指定日期 `%s` 没有账单'%bill_date} #TODO trans
            return self.return_json(404,data=err_msg)

        self.return_json(data=b.json())

@auth
class BillHisHandler(BaseCompanyHandler):

    def get(self,company_id):

        company = Company.objects.filter(Company.id == company_id).first()

        #TODO for test , uncomment the next two line for production
        if not self.check_relation_company(company):
           return

        bs = Bill.objects.filter(Bill.company_id==company_id).order_by(Bill.bill_date).all()
        his=[]
        for b in bs:
            his.append(b.json())

        self.return_json(data=his)