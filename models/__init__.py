#!/usr/bin/env python
#-*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-9
Email  : belongmyth at 163.com
'''

from base import init_db
from api import API, Service
from user import User, ApiKey, ApiKeyHis, InviteLog, ResetPassword
from company import Company, Employee,CompanyAlias
from role import Role, Permission
from bill import CDNServiceType,BillConfig,Bill
from product import ProductIns,Product,WebSite
from agent import Agent,AgentCompanyMap
from magic_login import MagicPass
from test import Node

from boss_models import BossChannel
from boss_models import BossDomain

from watermelong_models import WatermelonChannel
from watermelong_models import WatermelonDomain

def check_auth(key,handler):
    api = ApiKey.objects.filter(ApiKey.value == key).first()
    if not api:
        print 'key does not exist'
        return
    ps = api.user.role.permissions
    for p in ps:
        if p.api.handler == handler:
            break
    if p.api.handler == handler:
        print p
    else:
        print 'the key has no permission to access handler `%s`'%handler
