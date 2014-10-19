#!/usr/bin/python2.7
#-*- coding:utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.errors import MessageError

from log import logger
from settings import EMAIL_USER, EMAIL_PASS, EMAIL_HOST, EMAIL_PORT


class Mail(object):
    """
    邮件处理
    支持 HTML 标签处理
    使用： 需要发邮件的模块自定义并生成邮件内容
    """

    @classmethod
    def send(cls, to_list, subject, content):
        """
        to_list: 收件人列表
        subject: 邮件主题
        content: 邮件内容
        """
        content = content.encode('utf-8')
        frm = 'Tan14' + '<' + EMAIL_USER + '>'
        msg = MIMEText(content, _subtype='html', _charset='utf-8')
        msg['Subject'] = subject
        msg['From'] = frm
        msg['To'] = ';'.join(to_list)
        try:
            client = smtplib.SMTP()
            client.connect(EMAIL_HOST, EMAIL_PORT)
            client.login(EMAIL_USER, EMAIL_PASS)
            client.sendmail(frm, to_list, msg.as_string())
            client.close()
            return True
        except MessageError as e:
            logger.error('send email error:%s' % e)
            return False