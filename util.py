#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-9
Email  : belongmyth at 163.com
'''

import hashlib
import re
from datetime import datetime

from settings import TAN14_APP_ADDR
from mail import Mail
import random


email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
    r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)'  # domain
    r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)

RANDOM_SEED = 'abcdefghigklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~!@#$%^&*()_+-=[]{}|,./<>?'

def random_md5():

    s = ''.join([random.choice(RANDOM_SEED) for i in range(64)])
    randoms = hashlib.md5(s).hexdigest()
    return randoms


def generate_id():
    return random_md5()[8:30]


def generate_apikey():
    return random_md5()


def generate_invitekey():
    return random_md5()

def generate_resetkey():
    return random_md5()


def md5_value(s):
    assert isinstance(s, (str, unicode))
    return hashlib.md5(s).hexdigest()


def check_email(email):
    if email_re.match(email):
        return True
    return False

def check_tel(tel):
    return tel.isdigit()

def check_nickname(nickname):
    return len(nickname) <= 30

def send_email(email, subject, content):
    assert check_email(email), 'invalid email address:%s' % email
    return Mail.send([email], subject, content)


invite_subject_template = u'[TAN14] 邀请创建TAN14控制台用户 '

invite_conten_template = u'''
%(invite_company)s 邀请您创建TAN14帐户<br><br>

请点击下面的地址创建您的TAN14帐户：<br>
<a href="%(register_url)s" target="_blank">%(register_url)s</a> <br><br>

本邮件由TAN14系统自动发出，请勿直接回复！<br>
如有任何问题请联系电话：400-021-9900<br><br>

TAN14客服团队<br>
'''
def send_invite_email(invite_company,invited_user_email,invite_key):
    subject = invite_subject_template

    content = invite_conten_template % ({'invite_company': invite_company, 'register_url': '%s/reg/%s'%(TAN14_APP_ADDR,invite_key)})
    return send_email(invited_user_email, subject, content)

reset_subject_template  = u'[Tan14] TAN14密码重置邮件 '

reset_conten_template = u'''
尊敬的TAN14用户：<br><br>

请点击下面的地址重置你在TAN14的密码：<br>
<a href="%(reset_url)s" target="_blank">%(reset_url)s</a> <br><br>

本邮件由TAN14系统自动发出，请勿直接回复！<br>
如有任何问题请联系电话：400-021-9900<br><br>

TAN14客服团队<br>
'''

def send_reset_email(reset_user_email, reset_key):
    subject = reset_subject_template

    content = reset_conten_template % ({'reset_url': '%s/reset-password/%s'%(TAN14_APP_ADDR,reset_key)})
    return send_email(reset_user_email, subject, content)

#从二进制的低位开始
_AUTH_BIT_MAP = {
    'GET': 1,
    'POST': 2,
    'PUT': 3,
    'DELETE': 4,
    'HEAD': 5,
    'OPTIONS': 6
}


def check_permission(permission, method):
    if method.upper() not in _AUTH_BIT_MAP:
        return False
    p = bin(permission)[2:].zfill(10)
    return '1' == p[-1 * _AUTH_BIT_MAP[method.upper()]]


def get_permission(permission):
    ps = []
    for method in _AUTH_BIT_MAP:
        ps.append('%s:%s' % (method, 'Yes' if check_permission(permission, method) else 'No'))
    return ','.join(ps)

def trans_permission(method_dict):
    perm = [1, 1, 1, 1, 1, 1]
    for method in _AUTH_BIT_MAP:
        p = method_dict.get(method)
        perm[_AUTH_BIT_MAP[method] * -1] = '1' if p else '0'
    return int(''.join(perm),2)

def get_bill_date():
    now=datetime.now()
    _month = now.month
    if _month == 1:#如果当前时间为年初1月份,则要生成的账单应为上年末12月份
        year = now.year - 1
        month = 12
    else:
        year,month = (now.year,_month-1)
    return '%s%s'%(str(year),str(month).zfill(2))
