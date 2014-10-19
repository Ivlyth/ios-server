#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-9
Email  : belongmyth at 163.com
'''

from handlers.register import RegisterHandler,InviteRegisterHandler
from handlers.company import CompanysHandler, CompanyHandler, EmployeeHandler,CompanyChannelLogHandler,PnListHandler,DomainHandler
from handlers.user import LoginHandler, LogoutHandler, UserHandler, ForgetPasswordHandler
from handlers.user import RenewKeyHandler, CheckLoginHandler,ChangePasswdHandler
from handlers.auth import AuthHandler
from handlers.bill import BillHandler,BillHisHandler
from handlers.test import LoginHisHandler
from handlers.permission import PermissionsHandler,ServicesHandler,RoleHandler,ApisHandler
from handlers.accesslog import AccessLogHandler
from handlers.agent import AgentHandler
from handlers.useful import BlackIPHandler

from handlers.test import testHandler

root_url = ''  #'/account'

url_patterns = [
    # TEST
    (r'^%s/user/test/?$' % root_url, testHandler),

    # user
    # 用户注册 需Ｒoot角色
    (r'^%s/user/register/?$' % root_url, RegisterHandler),
    # 用户邀请注册 需 invite_key
    (r'^%s/user/register/(?P<invite_key>\w+)/?$'% root_url, InviteRegisterHandler),
    # 用户登陆
    (r'^%s/user/login/?$' % root_url, LoginHandler),
    # 用户登陆检查
    (r'^%s/user/login/check/?$' % root_url, CheckLoginHandler),
    # 用户信息查询/修改
    (r'^%s/user/(?P<user_id>\w{22})/?$' % root_url, UserHandler),
    # 退出登陆
    (r'^%s/user/(?P<user_id>\w{22})/logout/?$' % root_url, LogoutHandler),
    # renew api key
    (r'^%s/user/(?P<user_id>\w{22})/renewkey/?$' % root_url, RenewKeyHandler),
    # change password
    (r'^%s/user/(?P<user_id>\w{22})/password/?$' % root_url, ChangePasswdHandler),
    #(r'^%s/user/(?P<user_id>\w{22})/otherspassword?$' % root_url, ChangeOtherPasswdHandler),
    #(r'^%s/user/(?P<user_id>\w{22})/company?$' % root_url, UserCompanyHandler),
    # forget user password , send an reset email to user
    (r'^%s/user/password/forget/?$' % root_url, ForgetPasswordHandler), # POST
    # reset user password
    (r'^%s/user/password/reset/(?P<reset_key>\w+)/?$' % root_url, ForgetPasswordHandler), # PUT

    # company 创建公司
    (r'^%s/company/?$' % root_url, CompanysHandler),
    # 查询和更新公司
    (r'^%s/company/(?P<company_id>\w{22})/?$' % root_url, CompanyHandler),
    # 发起员工邀请注册
    (r'^%s/company/(?P<company_id>\w{22})/employee/invite/?$' % root_url, EmployeeHandler),
    # 删除员工
    (r'^%s/company/(?P<company_id>\w{22})/employee/(?P<employee_id>\w{22})/?$' % root_url, EmployeeHandler),
    # 公司日志
    # (r'^%s/company/(?P<company_id>\w{22})/log/?$' % root_url, CompanyLogHandler),
    # 公司某频道下日志
    (r'^%s/company/(?P<company_id>\w{22})/channel/(?P<channel_id>\w{22})/log/?$' % root_url, CompanyChannelLogHandler),
    # billing 当月账单和历史账单
    (r'^%s/company/(?P<company_id>\w{2,22})/bill/?(?P<bill_date>\d{6})?/?$' % root_url, BillHandler),
    (r'^%s/company/(?P<company_id>\w{2,22})/bill/his/?$' % root_url, BillHisHandler),

    # permissions
    (r'^%s/user/permission/?$'%root_url, PermissionsHandler),
    # login history
    (r'^%s/user/loginhis/?$'%root_url,LoginHisHandler),
    (r'^%s/user/permission/?'%root_url, PermissionsHandler),
    (r'^%s/user/service/?'%root_url, ServicesHandler),
    (r'^%s/user/role/?'%root_url, RoleHandler),
    (r'^%s/user/api/?'%root_url, ApisHandler),
    (r'^%s/permission/?'%root_url, PermissionsHandler),
    (r'^%s/permission/service/?'%root_url, ServicesHandler),
    (r'^%s/permission/role/?'%root_url, RoleHandler),
    (r'^%s/permission/api/?'%root_url, ApisHandler),
    (r'^%s/company/pnlist/?'%root_url, PnListHandler),
    (r'^%s/company/domain/?'%root_url, DomainHandler),

    (r'^%s/user/accesslog/?'%root_url, AccessLogHandler),
    #for 查看代理下pn列表
    (r'^%s/user/agent/?'%root_url, AgentHandler),

    (r'^%s/useful/autoblack/?'%root_url, BlackIPHandler),

    # auth 权限验证
    (r'^%s/authorization/?$' % root_url, AuthHandler)
]