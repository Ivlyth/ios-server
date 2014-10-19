#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-9-15
Email  : belongmyth at 163.com
'''

from base import BaseHandler
from models.role import Role,Permission
from models.api import Service,API
from util import trans_permission
from decorators.auth import auth

@auth
class RoleHandler(BaseHandler):

    def get(self):
        result = []
        roles = Role.objects.all()
        for role in roles:
            result.append(role.json())
        self.return_json(data=result)

    def _put_check(self):
        post_data = self.get_request_data()

        if 'id' not in post_data:
            err_msg = {'detail':'Must provide role id'}
            self.return_json(400,data = err_msg)
            return False

        if 'name' in post_data:
            pass

        if 'desc' in post_data:
            pass

        self.request_data = post_data
        return True

    def put(self):
        if not self._put_check():
            return

        name = self.request_data.get('name',None)
        desc = self.request_data.get('desc',None)
        role_id = self.request_data.get('id',None)
        role = Role.objects.filter(Role.id == role_id).first()
        if role is None:
            err_msg = {'detail':'Role does not exist'}
            return self.return_json(404,data=err_msg)

        if name is not None:
            role.name = name
        if desc is not None:
            role.desc = desc
        role.save()
        return self.return_json(200,data=role.json())

    def _post_check(self):
        post_data = self.get_request_data()

        if 'name' not in post_data:
            err_msg = {'detail':'Must provide role name'}
            self.return_json(400,data=err_msg)
            return False

        # do some check with role name TODO
        role = Role.objects.filter(Role.name == post_data['name']).first()
        if role is not None:
            err_msg = {'detail':'role name has already used'}
            self.return_json(400,data=err_msg)
            return False

        self.request_data = post_data
        return True

    def post(self):
        if not self._post_check():
            return
        name = self.request_data.get('name')
        desc = self.request_data.get('desc')
        role = Role(id=name,name=name,desc=desc)
        role.save()
        return self.return_json(data=role.json())

@auth
class PermissionsHandler(BaseHandler):

    def get(self):
        roles = Role.objects.all()
        ps = []
        for role in roles:
            ps.append(role.json(with_permissions=True))
        return self.return_json(data=ps)

    def _put_check(self):
        post_data = self.get_request_data()

        if 'id' not in post_data:
            err_msg = {'detail':'Must provide permission id'}
            self.return_json(400,data=err_msg)
            return False

        if 'GET' not in post_data:
            err_msg = {'detail':'Must provide permission `GET` value'}
            self.return_json(400,data=err_msg)
            return False

        if 'PUT' not in post_data:
            err_msg = {'detail':'Must provide permission `PUT` value'}
            self.return_json(400,data=err_msg)
            return False

        if 'POST' not in post_data:
            err_msg = {'detail':'Must provide permission `POST` value'}
            self.return_json(400,data=err_msg)
            return False

        if 'DELETE' not in post_data:
            err_msg = {'detail':'Must provide permission `DELETE` value'}
            self.return_json(400,data=err_msg)
            return False

        if 'HEAD' not in post_data:
            err_msg = {'detail':'Must provide permission `HEAD` value'}
            self.return_json(400,data=err_msg)
            return False

        if 'OPTIONS' not in post_data:
            err_msg = {'detail':'Must provide permission `OPTIONS` value'}
            self.return_json(400,data=err_msg)
            return False

        self.request_data = post_data
        return True

    def put(self):
        if not self._put_check():
            return

        id = self.request_data.get('id',None)

        method_dict = {
            'GET' : self.request_data.get('GET',None),
            'POST': self.request_data.get('POST',None),
            'PUT' : self.request_data.get('PUT',None),
            'DELETE' : self.request_data.get('DELETE',None),
            'HEAD' : self.request_data.get('HEAD',None),
            'OPTIONS': self.request_data.get('OPTIONS',None)
        }

        perm_value  = trans_permission(method_dict)
        permission = Permission.objects.filter(Permission.id == id).first()

        if permission is None:
            err_msg = {'detail':'permission does not exist'}
            self.return_json(400,data = err_msg)
            return

        permission.permission = perm_value
        permission.save()
        return self.return_json(data = permission.json())

    def _post_check(self):
        post_data = self.get_request_data()

        if 'api_id' not in post_data:
            err_msg = {'detail':'Must provide api id'}
            self.return_json(400,data=err_msg)
            return False

        if 'role_id' not in post_data:
            err_msg = {'detail':'Must provide role id'}
            self.return_json(400,data=err_msg)
            return False

        if 'GET' not in post_data:
            err_msg = {'detail':'Must provide permission `GET` value'}
            self.return_json(400,data=err_msg)
            return False

        if 'PUT' not in post_data:
            err_msg = {'detail':'Must provide permission `PUT` value'}
            self.return_json(400,data=err_msg)
            return False

        if 'POST' not in post_data:
            err_msg = {'detail':'Must provide permission `POST` value'}
            self.return_json(400,data=err_msg)
            return False

        if 'DELETE' not in post_data:
            err_msg = {'detail':'Must provide permission `DELETE` value'}
            self.return_json(400,data=err_msg)
            return False

        if 'HEAD' not in post_data:
            err_msg = {'detail':'Must provide permission `HEAD` value'}
            self.return_json(400,data=err_msg)
            return False

        if 'OPTIONS' not in post_data:
            err_msg = {'detail':'Must provide permission `OPTIONS` value'}
            self.return_json(400,data=err_msg)
            return False

        self.request_data = post_data
        return True

    def post(self):
        if not self._post_check():
            return

        api_id = self.request_data.get('api_id',None)
        role_id = self.request_data.get('role_id',None)

        method_dict = {
            'GET' : self.request_data.get('GET',None),
            'POST': self.request_data.get('POST',None),
            'PUT' : self.request_data.get('PUT',None),
            'DELETE' : self.request_data.get('DELETE',None),
            'HEAD' : self.request_data.get('HEAD',None),
            'OPTIONS': self.request_data.get('OPTIONS',None)
        }

        perm_value  = trans_permission(method_dict)
        permission = Permission(role_id=role_id,api_id=api_id,permission=perm_value)
        permission.save()
        return self.return_json(data = permission.json())

@auth
class ServicesHandler(BaseHandler):

    def get(self):
        result = []
        services = Service.objects.all()
        for s in services:
            result.append(s.json())
        self.return_json(data=result)

    def _put_check(self):
        post_data = self.get_request_data()
        if 'id' not in post_data:
            err_msg = {'detail':'Must provide service id'}
            self.return_json(400,data = err_msg)
            return False

        if 'name' in post_data:
            pass

        if 'desc' in post_data:
            pass

        self.request_data = post_data
        return True

    def put(self):
        if not self._put_check():
            return

        id = self.request_data.get('id',None)
        name = self.request_data.get('name',None)
        desc = self.request_data.get('desc',None)
        service = Service.objects.filter(Service.id == id).first()
        if service is None:
            err_msg = {'detail':'service does not exist'}
            return self.return_json(404,data=err_msg)
        if name is not None:
            service.name = name
        if desc is not None:
            service.desc = desc
        service.save()
        return self.return_json(data=service.json())

    def _post_check(self):
        post_data = self.get_request_data()
        if 'name' not in post_data:
            err_msg = {'detail':'Must provide service id'}
            self.return_json(400,data = err_msg)
            return False

        # do some check with service name

        self.request_data = post_data
        return True

    def post(self):
        if not self._post_check():
            return

        name = self.request_data.get('name')
        desc = self.request_data.get('desc')
        service = Service(name=name,desc=desc)
        service.save()
        return self.return_json(data=service.json())

@auth
class ApisHandler(BaseHandler):

    def get(self):
        result = []
        apis = API.objects.all()
        for a in apis:
            result.append(a.json())
        self.return_json(data=result)

    def _put_check(self):
        post_data = self.get_request_data()

        if 'id' not in post_data:
            err_msg = {'detail':'Must provide api id'}
            self.return_json(400,data = err_msg)
            return False

        self.request_data = post_data
        return True

    def put(self):
        if not self._put_check():
            return

        api_id = self.request_data.get('id',None)
        service_id = self.request_data.get('service_id',None)
        handler = self.request_data.get('handler',None)
        desc = self.request_data.get('desc',None)

        api = API.objects.filter(API.id == api_id).first()

        if api is None:
            err_msg = {'detail':'Api does not exist'}
            return self.return_json(404,data=err_msg)

        if service_id is not None:
            api.service_id = service_id
        if handler is not None:
            api.handler = handler
        if desc is not None:
            api.desc = desc

        api.save()
        return self.return_json(data = api.json())

    def _post_check(self):
        post_data = self.get_request_data()

        if 'service_id' not in post_data:
            err_msg = {'detail':'Must provide service id'}
            self.return_json(400,data=err_msg)
            return False

        service = Service.objects.filter(Service.id == post_data['service_id']).first()
        if service is None:
            err_msg = {'detail':'service does not exist'}
            self.return_json(400,data=err_msg)
            return False

        if 'handler' not in post_data:
            err_msg = {'detail':'Must provide handler name'}
            self.return_json(400,data=err_msg)
            return False

        self.request_data = post_data
        return True

    def post(self):
        if not self._post_check():
            return

        service_id = self.request_data.get('service_id',None)
        handler = self.request_data.get('handler',None)
        desc = self.request_data.get('desc',None)
        api = API(service_id=service_id,handler = handler, desc = desc)
        api.save()
        return self.return_json(data=api.json())