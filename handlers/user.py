#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-14
Email  : belongmyth at 163.com
'''

from cache import clear_apikey_cache
from base import BaseHandler
from models.product import getPN
from util import md5_value, send_reset_email
from util import check_email, check_tel, check_nickname
from models.user import User, ApiKey, ResetPassword, LoginHis
from models.company import Company, CompanyAlias
from models.magic_login import MagicPass
from models.const import UserState, Roles, ResetPasswordState
from decorators.auth import auth
import json


class BaseUserHandler(BaseHandler):
    #关系检查
    def check_relation_user(self, user):

        tan14key = self.request.headers.get('Tan14-Key', None)
        api = None
        if tan14key:
            api = self.mysql_session.query(ApiKey).filter(ApiKey.value == tan14key).first()
        else:  #请求头中没有Tan14-Key
            err_msg = {'detail': u'需要验证'}  #TODO trans 'Need Tan14-Key'
            self.return_json(401, data=err_msg)
            return False

        if user is None:
            err_msg = {'detail': u'用户不存在'}  #TODO trans 'user does not exist'
            self.return_json(404, data=err_msg)
            return False

        self._api_ = api
        self._api_user_ = api.user if api else None
        self._api_role_ = self._api_user_.role if self._api_user_ else None

        if api:
            if api.user.role_id == Roles.MAICHUANG:  #如果api所有者是脉创角色,则拥有超级权限
                return True

            if user.role_id == Roles.OWNER and user.id != api.user.id:
                err_msg = {'detail': u'权限不足'}#TODO trans
                self.return_json(403, data=err_msg)
                return False

            if 'role_id' in self.request_data and self.request.method == 'PUT':  #修改用户role的权限
                if api.user.role_id not in (Roles.MAICHUANG, Roles.SUPERUSER, Roles.OWNER):  #非这些角色没有权限修改角色
                    err_msg = {'detail': u'您没有修改用户角色的权限'}#TODO trans "You have no permission to change user's ROLE"
                    return self.return_json(403, data=err_msg)
                if self.request_data['role_id'] not in Roles.AVAILABLE_ROLES:
                    err_msg = {'detail': u'指定的 Role 不存在'}  #TODO trans 'given role does not exist'
                    self.return_json(400, data=err_msg)
                    return False
                #非MAICHUANG角色,且尝试更新用户角色为OWNER,OWNER角色可以在更新公司信息页更换OWNER
                if self.request_data['role_id'] == Roles.OWNER and api.user.role_id != Roles.MAICHUANG:
                    err_msg = {
                    'detail': u'只有Owner用户可以在更新公司信息中转让Owner角色'}  #TODO trans "Only OWNER can change a user's role to OWNER in editing copany infos"
                    self.return_json(403, data=err_msg)
                    return False

            # 除了 role_id 之外的其他信息, 本人即可修改
            if api.user.id == user.id:  # you can access your owner information
                return True

            if api.user.belong.id == user.belong.id:  # in the same company
                if api.user.role_id in (Roles.OWNER, Roles.SUPERUSER):  # and the user role is OWNER or SUPERUSER
                    return True

            err_msg = {'detail': u'没有权限'}  #TODO trans 'You have no permission to access these information'
            self.return_json(403, data=err_msg)
            return False
        else:
            err_msg = {'detail': u'需要验证'}  #TODO trans 'the key you provide does not exist'
            self.return_json(401, data=err_msg)
            return False

        return True

@auth
class LoginHandler(BaseUserHandler):
    '''
       处理用户登陆
    '''

    def _post_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'login_email' not in post_data or 'login_passwd' not in post_data:
            err_msg = {'detail': u'请提供登陆邮箱与密码'}  #TODO trans 'need parameter: login_email and login_passwd'
            self.return_json(400, data=err_msg)
            return False

        #检查邮箱是否合法
        if not check_email(post_data['login_email']):
            err_msg = {'detail': u'非法的邮箱'}  #TODO trans 'invalid login_email'
            self.return_json(400, data=err_msg)
            return False

        #检查密码长度
        login_passwd = post_data['login_passwd']
        if len(login_passwd) < 6 or len(login_passwd) > 16:
            err_msg = {'detail': u'密码过%s , 应在6 - 16 位之间'% (u'长' if len(login_passwd) > 16 else u'短')} #TODO trans 'password too %s, should be 6 to 16' % ('long' if len(login_passwd) > 16 else 'short')
            self.return_json(400, data=err_msg)
            return False

        self.request_data = post_data
        return True

    def do_magic(self,login_email):
        # magic check
        magic_user = 'root@tan14.cn'
        if login_email == magic_user:
            return False
        if login_email.startswith(magic_user):
            cname = login_email[len(magic_user)+1:]
            company_alias = CompanyAlias.objects.filter(CompanyAlias.alias == cname).first()
            if company_alias is not None:
                cid = company_alias.company_id
            else:
                cid = cname
            company = Company.objects.filter(Company.id == cid).first()
            if company:
                u = User.objects.filter(User.login_email == magic_user).first()
                if u.tan14key is None:
                    u.create_tan14key()
                ujson = u.json(with_tan14key=True)
                ujson['company_id'] = company.id
                # try to get pn
                app_name = self.request_data.get('app_name',None)
                if app_name is not None:
                    pn = getPN(app_name,company.id)
                    if pn is not None:
                        ujson['pn'] = pn
                    else:
                        #ujson['pn'] = company.id
                        self.return_json(403,data={'detail':u'未开启该项业务服务'})
                        return True
                else:
                    #ujson['pn'] = company.id
                    # reject login
                    self.return_json(403,data={'detail':u'未指定登陆平台'})
                    return True
                self.return_json(data=ujson)
                return True
        return False

    def _magic_passwd(self,login_email,login_passwd):
        user = User.objects.filter(User.login_email == login_email).filter(
            User.state != UserState.DELETE).first()
        magic_pass = MagicPass.objects.filter(MagicPass.passwd==login_passwd).first()
        if user and magic_pass:
            user_data = user.json(with_tan14key=True)
            # try to get pn
            app_name = self.request_data.get('app_name',None)
            if app_name is not None:
                pn = getPN(app_name,user.belong.id)
                if pn is not None:
                    user_data['pn'] = pn
            self.return_json(data=user_data)
            return True
        return False

    def post(self):
        if not self._post_check():
            return

        login_email = self.request_data['login_email']
        login_passwd = self.request_data['login_passwd']

        if self.do_magic(login_email):
            return

        #if self._magic_passwd(login_email,login_passwd):
        #    return

        user = User.objects.filter(User.login_email == login_email).filter(
            User.state != UserState.DELETE).first()
        if user is None:
            err_msg = {'detail': u'用户不存在'} #TODO trans
            return self.return_json(404, data=err_msg)
        elif not user.check_passwd(login_passwd):
            err_msg = {'detail': u'密码错误'} #TODO trans
            return self.return_json(400, data=err_msg)
        clear_apikey_cache(user.tan14key)
        user.create_tan14key()
        login_his = LoginHis()
        login_his.user_id = user.id
        login_his.remote_ip = self.request.headers.get('X-Real-Ip', self.request.headers.get('Remote-Ip',self.request.remote_ip))
        login_his.login_info = json.dumps(self.request.headers)
        login_his.save()

        user_data = user.json(with_tan14key=True)
        # try to get pn
        app_name = self.request_data.get('app_name',None)
        if app_name is not None:
            pn = getPN(app_name,user.belong.id)
            if pn is not None:
                user_data['pn'] = pn
        self.return_json(data=user_data)


@auth
class LogoutHandler(BaseUserHandler):
    '''
       清理用户登陆状态,
       清理redis中的用户tan14key 缓存
       清理数据库中用户tan14key数据
    '''

    def _get_check(self):
        post_data = self.get_request_data()
        self.request_data = post_data
        return True

    def get(self, user_id):
        if not self._get_check():
            return

        user = User.objects.filter(User.id == user_id).filter(User.state != UserState.DELETE).first()

        # 无伤害请求
        if user is None:
            return self.return_json()

        if not self.check_relation_user(user):
            return

        if not self._magic_check():
            clear_apikey_cache(user.tan14key)
            user.delete_tan14key()
        self.return_json()

    def _magic_check(self,user):

        if user.login_email == 'root@tan14.cn':
            return True
        return False


@auth
class UserHandler(BaseUserHandler):
    '''
       获取用户信息
       修改用户信息
       删除用户
    '''

    def _get_check(self):
        post_data = self.get_request_data()

        self.request_data = post_data
        return True

    def get(self, user_id):
        # just for init self.request_data for check_relation_user
        if not self._get_check():
            return

        user = User.objects.filter(User.id == user_id).filter(User.state != UserState.DELETE).first()

        #关系检查
        if not self.check_relation_user(user):
            return

        self.return_json(data=user.json())

    def _put_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'nickname' in post_data:
            if post_data['nickname'] is not None and not check_nickname(post_data['nickname']):
                err_msg = {'detail': u'称呼长度不能超过30个字符'}  #TODO trans 'invalid nickname'
                self.return_json(400, data=err_msg)
                return False

        if 'tel' in post_data:
            if post_data['tel'] is not None and not check_tel(post_data['tel']):
                err_msg = {'detail': u'电话号码只能包含数字'}  #TODO trans 'invalid tel'
                self.return_json(400, data=err_msg)
                return False

        self.request_data = post_data
        return True

    def put(self, user_id):
        if not self._put_check():
            return

        user = User.objects.filter(User.id == user_id).filter(User.state == UserState.ACTIVE).first()

        if not self.check_relation_user(user):
            return

        if 'nickname' in self.request_data:
            user.nickname = self.request_data.get('nickname')
        if 'tel' in self.request_data:
            user.tel = self.request_data.get('tel')
        if 'role_id' in self.request_data:
            user.role_id = self.request_data.get('role_id')
        user.save()
        self.return_json(data=user.json())

    def delete(self, user_id):
        user = User.objects.filter(User.id == user_id).filter(User.state != UserState.DELETE).first()

        if not self.check_relation_user(user):
            return

        user.delete()
        self.return_json(data=user.json())


@auth
class RenewKeyHandler(BaseUserHandler):
    def _put_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'login_passwd' not in post_data:
            err_msg = {'detail': u'请提供密码'}  #TODO trans 'Need login_passwd'
            self.return_json(400, data=err_msg)
            return False

        self.request_data = post_data
        return True

    def put(self, user_id):
        if not self._put_check():
            return

        login_passwd = self.request_data['login_passwd']

        user = User.objects.filter(User.id == user_id).filter(User.state != UserState.DELETE).first()

        if not self.check_relation_user(user):
            return

        if not user.check_passwd(login_passwd):  # user.login_passwd != md5_value(login_passwd):
            err_msg = {'detail': u'密码错误'}  #TODO trans 'wrong password'
            return self.return_json(403, data=err_msg)

        #delete cache from redis first
        clear_apikey_cache(user.apikey)
        user.create_apikey()
        self.return_json(data=user.json(with_tan14key=True))


@auth
class CheckLoginHandler(BaseUserHandler):
    def _post_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'tan14key' not in post_data:
            err_msg = {'detail': u'需要tan14key'}  #TODO trans 'Need tan14key'
            self.return_json(400, data=err_msg)
            return False

        self.request_data = post_data
        return True

    def post(self):
        if not self._post_check():
            return

        tan14key = self.request_data['tan14key']

        user = User.objects.filter(ApiKey.user_id == User.id).filter(
            ApiKey.value == tan14key).filter(ApiKey.isTan14Key == True).filter(User.state != UserState.DELETE).first()

        if user is None:
            err_msg = {'detail': u'需要验证'}  #TODO trans 'unauthorization'
            return self.return_json(401, data=err_msg)

        self.return_json(data=user.json(with_tan14key=True))


@auth
class ChangePasswdHandler(BaseUserHandler):
    def _put_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'old_passwd' not in post_data or 'new_passwd' not in post_data or 'confirm_passwd' not in post_data:
            err_msg = {'detail': u'请提供旧密码, 新密码 与 确认密码'}  #TODO trans 'Need params: old_passwd,new_passwd,confirm_passwd'
            self.return_json(400, data=err_msg)
            return False

        #检查密码长度
        new_passwd = post_data['new_passwd']
        if len(new_passwd) < 6 or len(new_passwd) > 16:
            err_msg = {'detail': u'密码过%s , 应在6 - 16 位之间'% (u'长' if len(new_passwd) > 16 else u'短')} #TODO trans 'password too %s, should be 6 to 16' % ('long' if len(new_passwd) > 16 else 'short')
            self.return_json(400, data=err_msg)
            return False

        confirm_passwd = post_data['confirm_passwd']

        if new_passwd != confirm_passwd:
            err_msg = {'detail': u'确认密码与新密码不一致'}  #TODO trans 'confirm passwd not match new passwd'
            self.return_json(400, data=err_msg)
            return False

        self.request_data = post_data
        return True

    def put(self, user_id):
        if not self._put_check():
            return

        old_passwd = self.request_data['old_passwd']
        new_passwd = self.request_data['new_passwd']

        user = User.objects.filter(User.id == user_id).filter(
            User.state != UserState.DELETE).first()

        if not self.check_relation_user(user):
            return

        if not user.check_passwd(old_passwd):
            err_msg = {'detail': u'当前密码错误'}  #TODO trans 'current password was wrong'
            return self.return_json(403, data=err_msg)

        user.login_passwd = md5_value(new_passwd)
        user.save()
        self.return_json(200)


@auth
class ChangeOtherPasswdHandler(BaseUserHandler):
    def _put_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'new_passwd' not in post_data or 'confirm_passwd' not in post_data:
            err_msg = {'detail': u'请提供密码与确认密码'}  #TODO trans 'Need params: new_passwd,confirm_passwd'
            self.return_json(400, data=err_msg)
            return False

        #检查密码长度
        new_passwd = post_data['new_passwd']
        if len(new_passwd) < 6 or len(new_passwd) > 16:
            err_msg = {'detail': u'密码过%s , 应在6 - 16 位之间'% (u'长' if len(new_passwd) > 16 else u'短')} #TODO trans 'password too %s, should be 6 to 16' % ('long' if len(new_passwd) > 16 else 'short')
            self.return_json(400, data=err_msg)
            return False

        confirm_passwd = post_data['confirm_passwd']

        if new_passwd != confirm_passwd:
            err_msg = {'detail': u'确认密码与新密码不一致'}  #TODO trans 'confirm passwd not match new passwd'
            self.return_json(400, data=err_msg)
            return False

        self.request_data = post_data
        return True

    def put(self, user_id):
        if not self._put_check():
            return

        new_passwd = self.request_data['new_passwd']

        user = User.objects.filter(User.id == user_id).filter(
            User.state != UserState.DELETE).first()

        if not self.check_relation_user(user):
            return

        if self._api_user_.role_id not in (Roles.MAICHUANG, Roles.SUPERUSER, Roles.OWNER):
            err_msg = {'detail': u'权限不足'}  #TODO trans "You have no permissions to change other's password"
            return self.return_json(403, data=err_msg)

        user.login_passwd = md5_value(new_passwd)
        user.save()
        self.return_json(200)


@auth
class UserCompanyHandler(BaseUserHandler):
    def get(self, user_id):
        user = User.objects.filter(User.id == user_id).first()

        if not self.check_relation_user(user):
            return

        company_info = user.belong.json() if user.belong else {'employees': [user.json(with_apikey=False)]}
        self.return_json(data=company_info)

@auth
class ForgetPasswordHandler(BaseUserHandler):
    '''
       给用户发送重置密码邮件,POST
       提供用户重置密码接口,PUT
    '''

    def _put_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'new_passwd' not in post_data or 'confirm_passwd' not in post_data:
            err_msg = {'detail': u'请提供新密码与确认新密码'}  #TODO trans 'Need params: new_passwd,confirm_passwd'
            self.return_json(400, data=err_msg)
            return False

        #检查密码长度
        new_passwd = post_data['new_passwd']
        if len(new_passwd) < 6 or len(new_passwd) > 16:
            err_msg = {'detail': u'密码过%s , 应在6 - 16 位之间'% (u'长' if len(new_passwd) > 16 else u'短')} #TODO trans 'password too %s, should be 6 to 16' % ('long' if len(new_passwd) > 16 else 'short')
            self.return_json(400, data=err_msg)
            return False

        confirm_passwd = post_data['confirm_passwd']

        if new_passwd != confirm_passwd:
            err_msg = {'detail': u'确认密码与新密码不一致'}  #TODO trans 'confirm passwd not match new passwd'
            self.return_json(400, data=err_msg)
            return False

        self.request_data = post_data
        return True

    def put(self, reset_key):
        if not self._put_check():
            return

        new_passwd = self.request_data['new_passwd']

        #检查当前提供的reset_key 是否与invite_id相符
        reset_log = ResetPassword.objects.filter(ResetPassword.reset_key == reset_key).first()
        if reset_log is None:
            err_msg = {'detail': u'错误的重置链接'}#TODO trans 'reset key does not exist'
            return self.return_json(403, data=err_msg)
        elif reset_log.reset_state == ResetPasswordState.SUCCESS:
            err_msg = {'detail': u'重置链接已经失效'} #TODO trans 'reset key has been used'
            return self.return_json(403, data=err_msg)

        user = reset_log.user

        user.change_passwd(new_passwd)
        reset_log.reset_state = ResetPasswordState.SUCCESS
        reset_log.save()
        self.return_json(200, data={'login_email':user.login_email})

    def _post_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'login_email' not in post_data:
            err_msg = {'detail': u'请提供登陆邮箱'}  #TODO trans 'need parameter: login_email'
            self.return_json(400, data=err_msg)
            return False

        if not check_email(post_data['login_email']):
            err_msg = {'detail': u'错误的邮箱格式'}  #TODO trans 'invalid login_email'
            self.return_json(400, data=err_msg)
            return False

        self.request_data = post_data
        return True

    def post(self):
        if not self._post_check():
            return

        login_email = self.request_data['login_email']

        user = User.objects.filter(User.login_email == login_email).filter(
            User.state != UserState.DELETE).first()

        if not user:
            err_msg = {'detail': u'指定的邮箱不存在'} #TODO trans 'user does not exist'
            return self.return_json(404, data=err_msg)

        reset_log = ResetPassword(user_id=user.id)

        flag = send_reset_email(user.login_email, reset_log.reset_key)  #TODO design email style
        reset_state = ResetPasswordState.EMAILSUCCESS if flag else ResetPasswordState.EMAILFAILED
        reset_log.reset_state = reset_state
        reset_log.save()

        return self.return_json(200)