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
