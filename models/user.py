# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-11
Email  : belongmyth at 163.com
'''
import hashlib
from datetime import datetime, timedelta

from sqlalchemy import Column, INTEGER, VARCHAR, DATETIME, BOOLEAN, ForeignKey, Enum, TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError

from base import BaseModel
from role import Role
from const import UserState, InviteState, Roles, ResetPasswordState
from util import generate_id, generate_apikey, md5_value,generate_invitekey,generate_resetkey
from settings import TAN14KEY_EXPIRE_SECONDS

Employee = None  #delay import


class User(BaseModel):
    __tablename__ = 'mc_user'

    id = Column('id', VARCHAR(40), primary_key=True)
    nickname = Column('nickname',VARCHAR(30)) #昵称
    login_email = Column('login_email', VARCHAR(50), unique=True)  #登陆邮箱
    login_passwd = Column('login_passwd', VARCHAR(40), nullable=False)  #登陆密码
    tel = Column('tel', VARCHAR(20))  # 电话
    role_id = Column('role_id', ForeignKey(Role.id), nullable=True)  #角色
    state = Column('state', Enum(*UserState.options), default=UserState.ACTIVE)  #状态
    invited_by = Column('invited_by', ForeignKey('mc_user.id'), nullable=True)  #邀请人
    created = Column('created',DATETIME,default=datetime.now)
    last_update = Column('last_updated',DATETIME,default=datetime.now)

    role = relationship(Role)

    _apikey = relationship('ApiKey')  # uselist=False

    @property
    def apikey(self):
        if len(self._apikey):
            for k in self._apikey:
                if not k.isTan14Key:
                    return k.value
        return None

    @property
    def tan14key(self):
        if len(self._apikey):
            for k in self._apikey:
                if k.isTan14Key:
                    return k.value
        return None

    def create_apikey(self):
        assert self.id is not None, 'call this func after save'
        apikeys = ApiKey.objects.filter(ApiKey.user_id == self.id).filter(ApiKey.isTan14Key == False).all()
        if apikeys:  #记录历史
            for oldapi in apikeys:
                his = ApiKeyHis(oldapi)
                his.save()
                self.session.delete(oldapi)
            self.session.commit()

        apikey = ApiKey(user_id=self.id)
        apikey.save()

    def delete_apikey(self):
        assert self.id is not None, 'call this func after save'
        apikeys = ApiKey.objects.filter(ApiKey.user_id == self.id).filter(ApiKey.isTan14Key == False).all()
        if apikeys:  #记录历史
            for oldapi in apikeys:
                his = ApiKeyHis(oldapi)
                his.save()
                self.session.delete(oldapi)
            self.session.commit()

    def create_tan14key(self):
        assert self.id is not None, 'call this func after save'
        apikeys = ApiKey.objects.filter(ApiKey.user_id == self.id).filter(ApiKey.isTan14Key == True).all()
        if apikeys:  #记录历史
            for oldapi in apikeys:
                his = ApiKeyHis(oldapi)
                his.save()
                self.session.delete(oldapi)
            self.session.commit()

        tan14key = ApiKey(user_id=self.id, isTan14Key=True)
        tan14key.save()

    def delete_tan14key(self):
        assert self.id is not None, 'call this func after save'
        apikeys = ApiKey.objects.filter(ApiKey.user_id == self.id).filter(ApiKey.isTan14Key == True).all()
        if apikeys:  #记录历史
            for oldapi in apikeys:
                his = ApiKeyHis(oldapi)
                his.save()
                self.session.delete(oldapi)
            self.session.commit()

    def set_role(self,role_name):
        self.role_id = role_name
        self.save()

    def save(self, commit=True):
        '''
        保存当前用户到数据库
        :param commit: 是否提交更改到数据库,默认为True
        :return:
        '''
        self.origin_passwd = self.login_passwd
        while True:  #防止生成重复id
            try:
                if self.id is None:  #从未保存过
                    self.id = generate_id()
                    self.login_passwd = md5_value(self.origin_passwd)
                    if self.role_id is None:
                        self.role_id = Roles.DEFAULT
                    self.session.add(self)
                self.last_update = datetime.now()
                if commit:
                    self.session.commit()
                break
            except IntegrityError as e:  #
                print '%s'%e
                self.logger.warn('found a duplicate user id %s'%self.id)
                self.session.rollback()
                self.id = None
        self.origin_passwd = None

    def check_passwd(self,passwd):
        return self.login_passwd == md5_value(passwd)

    def change_passwd(self,new_passwd):
        self.login_passwd = md5_value(new_passwd)
        self.save()

    def delete(self, commit=True):
        '''
        将当前用户状态改为 删除
        :param commit: 是否提交更改到数据库,默认为True
        :return:没有返回
        '''
        self.state = UserState.DELETE
        self.delete_apikey()
        self.delete_tan14key()
        self.save()

    def json(self, with_apikey=True, with_tan14key=False, with_company=False):
        assert self.id is not None, 'call this func after save'
        data = {
            'id': self.id,
            'login_email': self.login_email,
            'nickname':self.nickname,
            'tel': self.tel,
            'role_id':self.role_id,
            'company_id':self.belong.id if self.belong else None, # company_id
            'gravatar':hashlib.md5(self.login_email).hexdigest(),
            'created':self.created.strftime('%Y-%m-%d') if self.created else None,
            'last_update':self.last_update.strftime('%Y-%m-%d') if self.last_update else None,
            #'invite_by': self.invited_by
        }
        if with_apikey:
            data['apikey'] = self.apikey
        if with_tan14key:
            data['tan14key'] = self.tan14key
        if with_company:
            data['company'] = self.belong.json() if self.belong else None
        return data

    def __str__(self):
        return '<User(%s,role is %s)>' % (self.login_email, self.role.name)

    def __repr__(self):
        return self.__str__()

class LoginHis(BaseModel):
    __tablename__ = u'mc_login_his'

    id = Column('id',INTEGER,primary_key=True)
    user_id = Column('user_id',ForeignKey(User.id))
    login_date = Column('login_date', DATETIME, default=datetime.now)  # 创建时间
    remote_ip = Column('remote_ip', VARCHAR(50)) # 登陆地点IP地址
    login_info = Column('login_info', TEXT) # 登陆详细信息

    def save(self, commit = True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def json(self):
        data = {
            'user_id':self.user_id,
            'remote_ip':self.remote_ip,
            'login_info':self.login_info,
            'login_date':self.login_date.strftime('%Y-%m-%d %H:%M:%S')
        }
        return data

class ApiKey(BaseModel):
    __tablename__ = u'mc_apikey'

    value = Column('value', VARCHAR(40), primary_key=True)  # apikey value
    user_id = Column('user_id', ForeignKey(User.id))  # 所属用户
    created = Column('created', DATETIME, default=datetime.now)  # 创建时间
    isTan14Key = Column('istan14key', BOOLEAN, default=False)  # 是否因用户登陆Tan14网站而生成
    expire_at = Column('expire_at', DATETIME, default=datetime.max)  # 过期时间,Tan14key有默认过期时间

    user = relationship(User)

    def save(self, commit=True):
        while True:
            if self.value is None:
                self.value = generate_apikey()  # generate a random value
            if self.isTan14Key:
                self.expire_at = datetime.now() + timedelta(seconds=TAN14KEY_EXPIRE_SECONDS)
            try:
                self.session.add(self)
                if commit:
                    self.session.commit()
                break
            except IntegrityError as e:  # handler duplicate exception
                self.session.rollback()
                self.value = None

    @property
    def src(self):
        if self.isTan14Key:
            return u'Tan14Client'
        return u'Tan14API'

    def __str__(self):
        return '<ApiKey(%s,is %s,will expire at %s)>' % (self.value, self.src, self.expire_at)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def testdata2(cls):
        for u in User.objects.all():
            a = ApiKey(user_id=u.id)
            a.save()


class ApiKeyHis(BaseModel):
    __tablename__ = u'mc_apikey_his'

    value = Column('value', VARCHAR(40), primary_key=True)  # apikey value
    user_id = Column('user_id', ForeignKey(User.id))  # 所属用户
    created = Column('created', DATETIME)  # 创建时间
    isTan14Key = Column('istan14key', BOOLEAN, default=False)  # 是否因用户登陆Tan14网站而生成
    deleted = Column('deleted', DATETIME, default=datetime.now)  #删除时间

    user = relationship(User)

    def __init__(self, old_apikey):
        self.value = old_apikey.value
        self.user_id = old_apikey.user_id
        self.created = old_apikey.created
        self.isTan14Key = old_apikey.isTan14Key

    def save(self, commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

    @property
    def src(self):
        if self.isTan14Key:
            return u'Tan14Client'
        return u'Tan14API'

    def __str__(self):
        return '<ApiKeyHis(%s,is %s,deleted at %s)>' % (self.value, self.src, self.deleted)

    def __repr__(self):
        return self.__str__()


class InviteLog(BaseModel):
    __tablename__ = 'mc_invitelog'

    id = Column('id', INTEGER, primary_key=True)
    company_id = Column('company_id', ForeignKey('mc_company.id'), nullable=False)  #邀请人所在公司
    user_id = Column('user_id', ForeignKey(User.id), nullable=False)  #邀请人
    login_email = Column('login_email', VARCHAR(50), nullable=False)  #被邀请人邮箱
    invite_role = Column('invite_role',ForeignKey(Role.id),nullable=False) # 被邀请人被赋予的角色
    invite_key = Column('invite_key', VARCHAR(50), nullable=False)
    invite_date = Column('invite_date', DATETIME, default=datetime.now)  #邀请时间
    invite_state = Column('invite_state', Enum(*InviteState.options), nullable=False)  # 邮件发送失败/成功 用户查看邮件 用户成功注册 。。。

    user = relationship(User)

    def __init__(self,company_id,user_id,login_email,invite_role):
        self.company_id = company_id
        self.user_id = user_id
        self.login_email = login_email
        self.invite_role = invite_role
        self.invite_key = generate_invitekey()

    def save(self, commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def json(self):
        data = {
            'login_email' : self.login_email,
            'invite_date': self.invite_date.strftime('%Y-%m-%d') if self.invite_date else None
        }
        return data

    def __str__(self):
        return '<InviteLog(invited %s at %s with invite key %s)>' % (
            self.login_email, self.invite_date, self.invite_key)

    def __repr__(self):
        return self.__str__()


class ResetPassword(BaseModel):
    __tablename__ = 'mc_reset_password'

    id = Column('id', INTEGER, primary_key=True)
    user_id = Column('user_id', ForeignKey(User.id), nullable=False)  #申请重置密码用户
    reset_key = Column('reset_key', VARCHAR(50), nullable=False)
    reset_date = Column('reset_date', DATETIME, default=datetime.now)  #申请重置时间
    reset_state = Column('reset_state', Enum(*ResetPasswordState.options), nullable=False)  # 邮件发送失败/成功 用户查看邮件 用户成功重置密码 。。。

    user = relationship(User)

    def __init__(self,user_id):
        self.user_id = user_id
        self.reset_key = generate_resetkey()

    def save(self, commit=True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def __str__(self):
        return '<ResetPassword(`%s` reset password at %s with reset key %s)>' % (
            self.user.login_email, self.reset_date, self.reset_key)

    def __repr__(self):
        return self.__str__()

def delay_bind():
    '''
      bind `belong` to User
      it means which Company the user belong to
    '''
    from company import Employee, Company

    setattr(User, 'belong', relationship(Company, secondary=Employee.__table__, uselist=False))
    #secondaryjoin='join(User.id==Employee.employee_id).join(EmployeeState.DELETE!=Employee.state)'))


delay_bind()