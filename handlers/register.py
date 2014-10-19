#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-14
Email  : belongmyth at 163.com
'''

from base import BaseHandler
from models.company import Company
from models.user import User, InviteLog
from models.const import Roles,InviteState
from util import check_email,check_tel,check_nickname
from decorators.auth import auth

class BaseRegisterHandler(BaseHandler):
    def _post_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'login_email' not in post_data or 'login_passwd' not in post_data:
            err_msg = {'detail': u'请提供注册邮箱与密码'}  #TODO trans 'need parameter: login_email and login_passwd'
            self.return_json(400, data=err_msg)
            return False

        #检查邮箱是否合法
        if not check_email(post_data['login_email']):
            err_msg = {'detail': u'非法的邮箱地址'}  #TODO trans 'invalid login_email'
            self.return_json(400, data=err_msg)
            return False

        #检查密码长度
        login_passwd = post_data['login_passwd']
        if len(login_passwd)<6 or len(login_passwd)>16:
            err_msg={'detail':u'密码过%s , 应在6 - 16 位之间'% (u'长' if len(login_passwd) > 16 else u'短')} #TODO trans 'password too %s, should be 6 to 16'%('long' if len(login_passwd)>16 else 'short')
            self.return_json(400, data=err_msg)
            return False

        #检查tel是否合法
        if 'tel' in post_data:
            if not check_tel(post_data['tel']):#len(post_data['tel']) > 20:
                err_msg = {'detail': u'电话号码只能为纯数字'}  #TODO trans 'invalid tel'
                self.return_json(400, data=err_msg)
                return False

        #检查指定的role是否存在
        if 'role_id' in post_data:
            if post_data['role_id'] not in Roles.AVAILABLE_ROLES:
                err_msg = {'detail': u'指定的角色不存在'}  #TODO trans 'given role does not exist'
                self.return_json(400, data=err_msg)
                return False

        #检查邮箱是否已经注册过
        email_count = User.objects.filter(User.login_email == post_data['login_email']).count()
        if email_count > 0:
            err_msg = {'detail': u'邮箱已经被注册'}  #TODO trans 'login_email has already exist'
            self.return_json(409, data=err_msg)
            return False

        self.request_data = post_data
        return True


@auth
class RegisterHandler(BaseRegisterHandler):

    def post(self):
        if not self._post_check():
            return

        login_email = self.request_data['login_email']
        login_passwd = self.request_data['login_passwd']
        tel = self.request_data.get('tel', None)
        role_id = self.request_data.get('role_id', None)

        user = User(login_email=login_email, login_passwd=login_passwd, tel=tel, role_id=role_id)
        user.save()
        user.create_apikey()

        return self.return_json(201, data=user.json())

@auth
class InviteRegisterHandler(BaseRegisterHandler):

    def _post_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'login_passwd' not in post_data or 'confirm_passwd' not in post_data:
            err_msg = {'detail': u'请提供密码与确认密码'}  #TODO trans 'need parameter: login_passwd and confirm_passwd'
            self.return_json(400, data=err_msg)
            return False

        if post_data['login_passwd'] is not None and post_data['login_passwd']!=post_data['confirm_passwd']:
            err_msg = {'detail': u'确认密码与密码不一致'}  #TODO trans 'confirm password does not match login password'
            self.return_json(400, data=err_msg)
            return False

        if 'nickname' in post_data:
            if post_data['nickname'] is not None and not check_nickname(post_data['nickname']):
                err_msg = {'detail': u'称呼不能超过30个字符'} #TODO trans 'invalid nickname'
                return self.return_json(400,data=err_msg)

        if 'tel' in post_data:
            if post_data['tel'] is not None and not check_tel(post_data['tel']):
                err_msg = {'detail': u'电话号码只能为纯数字'} #TODO trans 'invalid tel'
                return self.return_json(400,data=err_msg)

        self.request_data = post_data
        return True

    def post(self, invite_key):
        if not self._post_check():
            return

        login_passwd = self.request_data['login_passwd']

        #检查当前提供的email是否与invite_id相符
        invitelog = InviteLog.objects.filter(InviteLog.invite_key == invite_key).first()
        if invitelog is None:
            err_msg = {'detail': u'邀请链接不存在' } # TODO trans 'invite key does not exist'
            return self.return_json(404, data=err_msg)
        elif invitelog.invite_state == InviteState.SUCCESS:
            err_msg = {'detail': u'邀请链接已失效'} #TODO trans 'invite key has been used'
            return self.return_json(403, data=err_msg)

        user = User(login_email=invitelog.login_email, login_passwd=login_passwd, role_id=invitelog.invite_role,
                    invited_by=invitelog.user_id)
        user.nickname = self.request_data.get('nickname',None)
        user.tel = self.request_data.get('tel',None)
        user.save()
        user.create_apikey()
        company = Company.objects.filter(Company.id == invitelog.company_id).first()
        company.addEmployee(user.id)
        invitelog.invite_state=InviteState.SUCCESS
        invitelog.save()

        return self.return_json(201, data={'login_email':user.login_email})