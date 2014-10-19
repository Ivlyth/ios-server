# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-12
Email  : belongmyth at 163.com
'''


class UserState:
    '''
      用户状态
    '''
    ACTIVE = 'Active'  # 正常可用
    LOCK = 'Lock'  # 锁定
    DELETE = 'Delete'  # 逻辑删除

    options = (ACTIVE, LOCK, DELETE)


class CompanyState:
    '''
       公司状态
    '''
    ACTIVE = 'Active'  # 正常
    DELETE = 'Delete'  # 逻辑删除

    options = (ACTIVE, DELETE)


class EmployeeState:
    ACTIVE = 'Active'
    LOCK = 'LOCK'
    DELETE = 'Delete'

    options = (ACTIVE, LOCK, DELETE)


class InviteState:
    '''
       邀请状态
    '''
    EMAILSUCCESS = 'EmailSuccess'  # 邀请邮件发送成功
    EMAILFAILED = 'EmailFailed'  # 邀请邮件发送失败
    ACCESSLINK = 'AccessLink'  # 访问邀请注册链接
    SUCCESS = 'Success'  # 邀请注册成功

    options = (EMAILFAILED, EMAILSUCCESS, ACCESSLINK, SUCCESS)

class ResetPasswordState:
    '''
       邀请状态
    '''
    EMAILSUCCESS = 'EmailSuccess'  # 重置邮件发送成功
    EMAILFAILED = 'EmailFailed'  # 重置邮件发送失败
    ACCESSLINK = 'AccessLink'  # 访问重置链接
    SUCCESS = 'Success'  # 重置成功

    options = (EMAILFAILED, EMAILSUCCESS, ACCESSLINK, SUCCESS)


class Roles:
    '''
    user - Can only access analytics.
    billing - Grants access to billing.
    engineer - Grants access to the config panel.
    superuser - Full company access.
    '''
    MAICHUANG = 'Root'
    OWNER = 'Owner'
    SUPERUSER = 'SuperUser'
    BILLING = 'Billing'
    ENGINEER = 'Engineer'
    USER = 'User'

    _MAICHUANG = ('Root', 'Be used internally')
    _OWNER = ('Owner', 'Can only access analytics.')
    _SUPERUSER = ('SuperUser', 'Full company access.')
    _BILLING = ('Billing', 'Grants access to billing.')
    _ENGINEER = ('Engineer', 'Grants access to the config panel.')
    _USER = ('User', 'Can only access analytics.')

    CHOICES = (_MAICHUANG, _OWNER, _SUPERUSER, _BILLING, _ENGINEER, _USER)

    AVAILABLE_ROLES = (MAICHUANG, OWNER, SUPERUSER, BILLING, ENGINEER, USER)

    DEFAULT = USER


class Services:

    BOSS = 'BOSS'
    MCACCOUNT = 'MCACCOUNT'

    CHOICES = (BOSS, MCACCOUNT)


class CDNServices:
    #(NAME,VERBOSE_NAME, DESC, IS_GRADUATED, GRADUATED_CONFIG),
    _T_FZ = ('T_FZ', u'峰值计费', u'所有带宽数据点降序排列，取第一值', False, None)
    _T_QSF = ('T_QSF', u'去三峰', u'所有带宽数据点降序排列,取第四值', False, None)
    _T_QSF_2 = ('T_QSF_2', u'去三天峰值', u'每天取一个最大带宽点,降序排列,取第四值', False, None)
    _T_95 = ('T_95', u'95计费', u'所有带宽数据点降序排列，剔除前5%的数据点，取第一值', False, None)
    _T_95_2 = ('T_95_2', u'峰值95%', u'所有带宽数据点降序排列，取第一值*95%', False, None)
    _T_RFJT = ('T_RFJT', u'日峰值阶梯', u'每天取一个最大带宽点，分3个梯度算应付款，求和', True, {})
    _T_PJDK = ('T_PJDK', u'平均带宽', u'所有的带宽数据求和/数据点数', False, None)
    _T_10PFZPJ = ('T_10PFZPJ', u'10%峰值平均', u'所有带宽数据点降序排列，取前10%的数据点，求平均带宽', False, None)
    _T_FQ = ('T_FQ', u'分区计费', u'按省95计费，费用求和', False, None)
    _T_LL = ('T_LL', u'流量计费', u'流量总和', False, None)
    _T_MAN = ('T_MAN', u'手工出账', u'人工计算账单上传', False, None)

    T_FZ = 'T_FZ'
    T_QSF = 'T_QSF'
    T_QSF_2 = 'T_QSF_2'
    T_95 = 'T_95'
    T_95_2 = 'T_95_2'
    T_RFJT = 'T_RFJT'
    T_PJDK = 'T_PJDK'
    T_10PFZPJ = 'T_10PFZPJ'
    T_FQ = 'T_FQ'
    T_LL = 'T_LL'
    T_MAN = 'T_MAN'

    CHOICES = (_T_FZ, _T_QSF, _T_QSF_2, _T_95, _T_95_2, _T_RFJT, _T_PJDK, _T_10PFZPJ, _T_FQ, _T_LL, _T_MAN)

    AVAILABLE_SERVICE_TYPES = (T_FZ, T_QSF, T_QSF_2, T_95, T_95_2, T_RFJT, T_PJDK, T_10PFZPJ, T_FQ, T_LL, T_MAN)

    TRAFFIC = (T_LL,) #流量计费方式
    BANDWIDTH = (T_FZ, T_QSF, T_QSF_2, T_95, T_95_2, T_RFJT, T_PJDK, T_10PFZPJ, T_FQ)#带宽计费方式

class ProductState:
    ACTIVE = 'Active'
    DELETE = 'Delete'

    options = (ACTIVE, DELETE)

class ProductInsState:
    ACTIVE = 'Active'
    DELETE = 'Delete'

    options = (ACTIVE, DELETE)