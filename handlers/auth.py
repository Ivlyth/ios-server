#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-14
Email  : belongmyth at 163.com
'''

from datetime import datetime

from base import BaseHandler
from cache import (set_apikey_cache, get_apikey_cache, set_apikey_info_cache, get_apikey_info_cache, set_cache_expire,
                   reset_cache_expire, is_persist)
from models.user import ApiKey, User
from models.role import Role, Permission
from models.api import API, Service
from util import check_permission
from log import store_access_log
from tornado import gen
from tornado.concurrent import Future


class AuthHandler(BaseHandler):
    def _post_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        # if 'tan14key' not in post_data \
        #         or 'service' not in post_data \
        #         or 'handler' not in post_data \
        #         or 'method' not in post_data:
        #     return False

        self.request_data = post_data
        return True

    def _not_need_auth_check(self,tan14key, service, handler):
        future = Future()
        if tan14key is None:#没有提供 tan14key
            s = Service.objects.filter(Service.name == service).first()
            if s is None:
                future.set_result(False)
                return future
            api = API.objects.filter(API.service_id == s.id).filter(API.handler == handler).first()
            if api is None:# api 不存在
                future.set_result(False)
                return future
            permission = Permission.objects.filter(Permission.api_id == api.id).first()
            if permission is None:
                future.set_result(True)
                return future
        future.set_result(False)
        return future

    @gen.coroutine
    def post(self):
        if not self._post_check():
            self.set_status(401)
            self.need_store_access_log = False  #这种情况下不需要记录访问日志
            return

        self.need_store_access_log = True
        self.request.access_logdata={}

        tan14key = self.request_data.get('tan14key',None)
        service = self.request_data['service']
        handler = self.request_data['handler']
        method = self.request_data['method']

        self.request.access_logdata.update(self.request_data)

        r = yield self._not_need_auth_check(tan14key, service, handler)
        if r:
            self.request.access_logdata['access_result'] = 'NOT_NEED_AUTH'  #验证结果 PASS
            self.set_status(200)
            return

        dr = yield self._do_check(tan14key, service, handler, method)

    def _do_check(self,tan14key, service, handler, method):

        future = Future()
        future.set_result(False)
        # check cache
        permission = get_apikey_cache(tan14key, service, handler)
        if permission is not None:
            apiinfo = get_apikey_info_cache(tan14key)
            user_id , login_email, company_id = apiinfo.split('_')
            self.request.access_logdata['user_id'] = user_id
            self.request.access_logdata['login_email'] = login_email
            self.request.access_logdata['company_id'] = company_id
            self.request.access_logdata['istan14key'] = 'No' if is_persist(tan14key) else 'Yes'
            if not check_permission(int(permission), method):
                #if it's a client key , reset the expire time
                if not is_persist(tan14key):
                    reset_cache_expire(tan14key)
                #self.write('MUST RETURN SOMETHING?')
                self.request.access_logdata['access_result'] = 'DENIED'  #验证结果 DENIED
                self.set_status(401)
                return future
            else:
                self.request.access_logdata['access_result'] = 'PASS'  #验证结果 PASS
                self.set_status(200)
                future.set_result(True)
                return future
        else:
            # 查找
            p_and_a = self.mysql_session.query(Permission, ApiKey). \
                filter(ApiKey.user_id == User.id). \
                filter(User.role_id == Role.id). \
                filter(Permission.role_id == Role.id). \
                filter(Permission.api_id == API.id). \
                filter(API.service_id == Service.id). \
                filter(ApiKey.value == tan14key). \
                filter(Service.name == service). \
                filter(API.handler == handler). \
                first()
                # filter(ApiKey.expire_at > datetime.now()). \

            if not p_and_a:  #如果提供的数据在数据库中不存在
                self.set_status(401)
                self.request.access_logdata['access_result'] = 'DENIED'  #验证结果 DENIED
                return future

            p, a = p_and_a #permission and api
            #记录相关信息
            user_id = a.user.id
            login_email = a.user.login_email
            company_id = a.user.belong.id if a.user.belong else ''
            #将数据写入缓存
            set_apikey_cache(tan14key, service, handler, p.permission)
            set_apikey_info_cache(tan14key, user_id, login_email, company_id)
            #对client key 设置过期时间
            if a.isTan14Key:
                set_cache_expire(tan14key)

            # self.request.access_logdata['handler_desc'] = p.api.desc
            self.request.access_logdata['user_id'] = user_id
            self.request.access_logdata['login_email'] = login_email
            self.request.access_logdata['company_id'] = company_id
            self.request.access_logdata['istan14key'] = 'No' if not a.isTan14Key else 'Yes'

            if not p.check(method):  #没有权限
                self.set_status(401)
                self.request.access_logdata['access_result'] = 'DENIED'  #验证结果 DENIED
                return future

            self.request.access_logdata['access_result'] = 'PASS'  #验证结果 PASS
            self.set_status(200)
            future.set_result(True)
            return future

    def on_finish(self):
        if not self.need_store_access_log:
            return
        store_access_log(self.request)


'''

SELECT
 mc_role_permission.role AS mc_role_permission_role,
 mc_role_permission.api AS mc_role_permission_api,
 mc_role_permission.id AS mc_role_permission_id,
 mc_role_permission.permission AS mc_role_permission_permission,

 mc_apikey.istan14key AS mc_apikey_istan14key,
 mc_apikey.value AS mc_apikey_value,
 mc_apikey.user_id AS mc_apikey_user_id,
 mc_apikey.created AS mc_apikey_created,
 mc_apikey.expire_at AS mc_apikey_expire_at
    FROM mc_role_permission,
         mc_apikey,
         mc_user,
         mc_role,
         mc_apilist,
         mc_service
    WHERE mc_apikey.user_id = mc_user.id
    AND mc_user.role_id = mc_role.id
    AND mc_role_permission.role = mc_role.id
    AND mc_role_permission.api = mc_apilist.id
    AND mc_apilist.service_id = mc_service.id
    AND mc_apikey.expire_at > %s(2014, 7, 16, 17, 3, 46, 528928)
    AND mc_apikey.value = %s mythapikey
    AND mc_service.name = %s MythService
    AND mc_apilist.handler = %s mythhandler
     LIMIT %s 1

'''