#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-9-28
Email  : belongmyth at 163.com
'''

from base import BaseHandler
from log.mongo import get_access_log

class AccessLogHandler(BaseHandler):

    def get(self):
        self.request_data = self.get_request_data()
        handler = self.request_data.get('handler',None)
        fields = self.request_data.get('fields',None)
        if handler is None:
            return
        query = {
            'handler':{
                '$in':handler.split(',')
            }
        }
        if fields is None:
            fields_list = None
        else:
            fields_list = {}
            for f in fields.split(','):
                fields_list[f] = 1
        print query
        print fields_list
        cursor = get_access_log(query,fields_list)
        result = []
        for c in cursor:
            if 'access_date' in c:
                c['access_date'] = c['access_date'].strftime('%Y-%m-%d %H:%M:%S')
            result.append(c)
        return self.return_json(data=result)