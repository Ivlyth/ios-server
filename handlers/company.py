#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-14
Email  : belongmyth at 163.com
'''

from datetime import datetime

from base import BaseHandler
from models.company import Company, Employee
from models.product import ProductIns
from models.user import User, InviteLog, ApiKey
from models.const import CompanyState, EmployeeState, InviteState, Roles
from cache import clear_apikey_cache
from util import check_email,check_tel, send_invite_email
from log.mongo import get_access_log_by_company,get_access_log_by_channel_no_page

from decorators.auth import auth

class BaseCompanyHandler(BaseHandler):
    #关系检查
    def check_relation_company(self, company):

        tan14key = self.request.headers.get('Tan14-Key', None)
        api = None
        if tan14key:
            api = self.mysql_session.query(ApiKey).filter(ApiKey.value == tan14key).first()
        else:  #请求头中没有Tan14-Key
            err_msg = {'detail':u'需要认证' }  #TODO trans 'Need Tan14-Key'
            self.return_json(401, data=err_msg)
            return False

        if company is None:
            err_msg = {'detail': u'公司不存在'}  #TODO trans
            self.return_json(404, data=err_msg)
            return False

        self._api_ = api
        self._api_user_ = api.user if api else None
        self._api_role_ = self._api_user_.role if self._api_user_ else None

        if api:
            if api.user.role_id == Roles.MAICHUANG:  #如果是脉创角色,则拥有超级权限
                return True
            #if api.user.id != company.owner_id:# or api.user.role.name == Roles.SUPERUSER
            if api.user.belong.id != company.id:
                err_msg = {'detail': u'公司不存在'}  #TODO trans 'You can only access your own company information'
                self.return_json(404, data=err_msg)
                return False
            if self.request.method == 'PUT' :
                if api.user.role_id not in (Roles.SUPERUSER,Roles.OWNER):
                    err_msg = {'detail': u'权限不足'}  #TODO trans 'You have no permission to do the action'
                    self.return_json(403, data=err_msg)
                    return False
        else:
            err_msg = {'detail': u'需要认证'}  #TODO trans 'the key you provide does not exist'
            self.return_json(401, data=err_msg)
            return False

        return True

    #关系检查
    def check_relation_company_employee(self, company, employee):

        if company is None:
            err_msg = {'detail': u'公司不存在'}  #TODO trans 'company does not exist'
            self.return_json(404, data=err_msg)
            return False

        if employee is None:
            err_msg = {'detail': u'员工不存在'}  #TODO trans 'employee does not exist'
            self.return_json(404, data=err_msg)
            return False

        tan14key = self.request.headers.get('Tan14-Key', None)
        api = None
        if tan14key:
            api = self.mysql_session.query(ApiKey).filter(ApiKey.value == tan14key).first()
        else:  #请求头中没有Tan14-Key
            err_msg = {'detail': u'需要认证'}  #TODO trans 'Need Tan14-Key'
            self.return_json(401, data=err_msg)
            return False

        self._api_ = api
        self._api_user_ = api.user if api else None
        self._api_role_ = self._api_user_.role if self._api_user_ else None

        if api:
            if api.user.role_id == Roles.MAICHUANG:  #如果是脉创角色,则拥有超级权限
                return True
            #if api.user.id != company.owner_id:# or api.user.role.name == Roles.SUPERUSER
            if api.user.belong.id != company.id:
                err_msg = {'detail': u'公司不存在'}  #TODO trans 'You can only access your own company information'
                self.return_json(404, data=err_msg)
                return False
            if api.user.role_id not in (Roles.SUPERUSER,Roles.OWNER):
                err_msg = {'detail': u'权限不足' }  #TODO trans 'You have no permission to do the action'
                self.return_json(403, data=err_msg)
                return False
            if company.id != employee.company_id:  #员工非该公司名下
                err_msg = {'detail': u'员工不存在'}  #TODO trans 'You can only access your own employees information'
                self.return_json(404, data=err_msg)
                return False
        else:
            err_msg = {'detail': u'需要认证'}  #TODO trans 'the key you provide does not exist'
            self.return_json(401, data=err_msg)
            return False

        return True


@auth
class CompanysHandler(BaseCompanyHandler):
    def _post_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'name' not in post_data:
            err_msg = {'detail': u'请至少提供公司名称'}  #TODO trans 'need parameter: name'
            self.return_json(400, data=err_msg)
            return False

        #检查公司是否已经存在
        company_count = Company.objects.filter(Company.name == post_data['name']).count()
        if company_count == 1:
            err_msg = {'detail': u'公司名称已存在'}  #TODO trans 'company has already exist'
            self.return_json(409, data=err_msg)
            return False

        #检查tel是否合法
        if 'tel' in post_data:
            if post_data['tel'] is not None and not check_tel(post_data['tel']):
                err_msg = {'detail': u'电话号码只能包含数字'}  #TODO trans 'invalid tel'
                self.return_json(400, data=err_msg)
                return False

        #检查addr是否合法
        if 'addr' in post_data:
            if post_data['addr'] is not None and len(post_data['addr']) > 100:
                err_msg = {'detail': u'地址长度需小于100个字符'}  #TODO trans
                self.return_json(400, data=err_msg)
                return False

        #检查指定的User是否存在
        if 'owner_id' in post_data:
            owner = User.objects.filter(User.id == post_data['owner_id']).first()
            if owner is None:
                err_msg = {'detail': u'指定的Owner用户不存在'}  #TODO trans 'given owner id does not exist'
                self.return_json(400, data=err_msg)
                return False
            elif owner.role_id != Roles.OWNER:#如果指定的用户角色非OWNER
                err_msg = {'detail': u'请先更改指定Owner用户的角色至Owner'}  #TODO trans "change the given user's ROLE to `OWNER` first"
                self.return_json(403, data=err_msg)
                return False

        #检查指定的User是否存在
        if 'biller_id' in post_data:
            biller = User.objects.filter(User.id == post_data['biller_id']).first()
            if biller is None:
                err_msg = {'detail': u'指定的账单联系人不存在'}  #TODO trans 'given billing id does not exist'
                self.return_json(400, data=err_msg)
                return False
            elif biller.role_id != Roles.BILLING:#如果指定的用户角色非BILLING
                err_msg = {'detail': u'请先更改指定账单联系人的角色至Billing'}  #TODO trans "change the given user's ROLE to `BILLING` first"
                self.return_json(400, data=err_msg)
                return False


        #检查service_start是否合法
        if 'service_start' in post_data:
            try:
                service_start = datetime.strptime(post_data['service_start'], '%Y%m%d')
                post_data['service_start'] = service_start
            except ValueError as e:
                err_msg = {'detail': u'非法的服务开始时间'}  #TODO trans 'invalid service_start,'
                self.return_json(400, data=err_msg)
                return False

        #检查service_end是否合法
        if 'service_end' in post_data:
            try:
                service_end = datetime.strptime(post_data['service_end'], '%Y%m%d')
                post_data['service_end'] = service_end
            except ValueError as e:
                err_msg = {'detail': u'非法的服务结束时间'}  #TODO trans 'invalid service_end,'
                self.return_json(400, data=err_msg)
                return False

        #服务开始时间不能大于结束时间
        if 'service_start' in post_data and 'service_end' in post_data:
            if post_data['service_start'] > post_data['service_end']:
                err_msg = {'detail': u'服务开始时间不能在服务结束时间之后'}  #TODO trans 'service_start cannot be greater than service_end'
                self.return_json(400, data=err_msg)
                return False

        self.request_data = post_data
        return True

    def post(self):
        if not self._post_check():
            return

        name = self.request_data['name']
        addr = self.request_data.get('addr', None)
        tel = self.request_data.get('tel', None)
        owner_id = self.request_data.get('owner_id', None)
        biller_id = self.request_data.get('biller_id', None)
        service_start = self.request_data.get('service_start', None)
        service_end = self.request_data.get('service_end', None)

        company = Company(name=name, addr=addr, tel=tel, owner_id=owner_id, biller_id=biller_id,
                          service_start=service_start, service_end=service_end)
        company.save()

        if owner_id is not None:
            company.addEmployee(owner_id)
        if biller_id is not None:
            company.addEmployee(biller_id)

        return self.return_json(201, data=company.json())

    def get(self):
        companys = Company.objects.filter(Company.state != CompanyState.DELETE).all()
        cs = []
        for c in companys:
            cs.append(c.json())
        self.return_json(data=cs)


@auth
class CompanyHandler(BaseCompanyHandler):
    def _put_check(self):
        post_data = self.get_request_data()

        #检查tel是否合法
        if 'tel' in post_data:
            if post_data['tel'] is not None and not check_tel(post_data['tel']):
                err_msg = {'detail': u'电话号码只能包含数字'}  #TODO trans 'invalid tel,must be only contains numbers'
                self.return_json(400, data=err_msg)
                return False

        #检查addr是否合法
        if 'addr' in post_data:
            if post_data['addr'] is not None and len(post_data['addr']) > 100:
                err_msg = {'detail': u'地址长度需小于100字符'}  #TODO trans 'invalid addr,addr length cant be greater than 100'
                self.return_json(400, data=err_msg)
                return False

        #检查指定的User是否存在
        if 'owner_id' in post_data:
            owner = User.objects.filter(User.id == post_data['owner_id']).first()
            if owner is None:
                err_msg = {'detail': u'指定的Owner用户不存在'}  #TODO trans 'given owner id does not exist'
                self.return_json(400, data=err_msg)
                return False

        #检查service_start是否合法
        if 'service_start' in post_data:
            try:
                service_start = datetime.strptime(post_data['service_start'], '%Y-%m-%d')
                post_data['service_start'] = service_start
            except ValueError as e:
                err_msg = {'detail': u'非法的服务开始时间'}  #TODO trans 'invalid service_start'
                self.return_json(400, data=err_msg)
                return False

        #检查service_end是否合法
        if 'service_end' in post_data:
            try:
                service_end = datetime.strptime(post_data['service_end'], '%Y-%m-%d')
                post_data['service_end'] = service_end
            except ValueError as e:
                err_msg = {'detail': u'非法的服务结束时间'}  #TODO trans 'invalid service_end'
                self.return_json(400, data=err_msg)
                return False

        #服务开始时间不能大于结束时间
        if 'service_start' in post_data and 'service_end' in post_data:
            if post_data['service_start'] > post_data['service_end']:
                err_msg = {'detail': u'服务开始时间不能晚于服务结束时间'}  #TODO trans 'service_start cannot be greater than service_end'
                self.return_json(400, data=err_msg)
                return False

        self.request_data = post_data
        return True

    def put(self, company_id):
        if not self._put_check():
            return

        company = Company.objects.filter(Company.id == company_id).first()

        #关系检查
        if not self.check_relation_company(company):
            return

        addr = self.request_data.get('addr', None)
        tel = self.request_data.get('tel', None)
        owner_id = self.request_data.get('owner_id', None)
        #biller_id = self.request_data.get('biller_id', None)
        service_start = self.request_data.get('service_start', None)
        service_end = self.request_data.get('service_end', None)

        #只有owner可以变更owner
        #如果指定了新的owner，将之前的owner角色更新为superuser
        change_owner = False
        if owner_id:
            if self._api_user_.role_id not in (Roles.MAICHUANG,Roles.OWNER):#如果是非MAICHUANG 或者 OWNER
                err_msg = {'detail': u'只有当前Owner用户可以修改公司Owner'} #TODO trans 'Only current Owner can change owner to other'
                return self.return_json(403,data=err_msg)
            # 修改OWNER
            if company.owner_id != owner_id:
                company.owner.set_role(Roles.SUPERUSER)# 将之前的owner角色变更为 SUPERUSER
                company.owner_id = owner_id
                change_owner = True
        #如果指定了新的biller，将之前的biller角色更新为user
        # if biller_id:
        #     if company.biller_id:
        #         company.biller.set_role(Roles.USER)
        #     company.biller_id=biller_id

        if addr is not None:
            company.addr = addr
        if tel is not None:
            company.tel = tel
        if service_start is not None:
            company.service_start = service_start
        if service_end is not None:
            company.service_end = service_end
        company.save()
        if change_owner:
            company.owner.set_role(Roles.OWNER)

        return self.return_json(200, data=company.json())

    def get(self, company_id):
        company = Company.objects.filter(Company.id == company_id).filter(Company.state != CompanyState.DELETE).first()

        #关系检查
        if not self.check_relation_company(company):
            return

        self.return_json(data=company.json())


@auth
class EmployeeHandler(BaseCompanyHandler):
    def delete(self, company_id, employee_id):

        #find the employee belong the given company
        company = employee = None
        c_and_e = self.mysql_session.query(Company, Employee).filter(Company.id == company_id). \
            filter(Employee.employee_id == employee_id).first()
        if c_and_e:
            company, employee = c_and_e
            if not self.check_relation_company_employee(company, employee):
                return
        else:
            err_msg = {'detail': u'指定员工不存在'}  #TODO trans 'employee does not exist'
            return self.return_json(404, data=err_msg)

        if company.owner_id == employee_id:
            err_msg = {'detail': u'不能删除公司Owner'}  #TODO trans 'can not delete company owner'
            return self.return_json(403, data=err_msg)

        employee.delete() #将员工状态置为删除
        clear_apikey_cache(employee.user.tan14key) #清除用户相关的缓存
        employee.user.delete() #将对应用户删除

        self.return_json()#data=employee.user.json() 只返回200 http code

    def get(self,company_id):
        company = Company.objects.filter(Company.id == company_id).filter(Company.state != CompanyState.DELETE).first()

        if not self.check_relation_company(company):
            return

        inviteHis = InviteLog.objects.filter(InviteLog.company_id == company_id).filter(InviteLog.invite_state != InviteState.SUCCESS).all()
        ihs = []
        for ih in inviteHis:
            ihs.append(ih.json())
        self.return_json(data=ihs)

    def _post_check(self):
        post_data = self.get_request_data()
        #检查必须的参数
        if 'login_email' not in post_data or 'role_id' not in post_data:
            err_msg = {'detail': u'请提供待邀请用户的邮箱与邀请成为的角色'}  #TODO trans 'need parameter: login_email and role_id'
            self.return_json(400, data=err_msg)
            return False

        #检查邮箱是否合法
        if not check_email(post_data['login_email']):
            err_msg = {'detail': u'非法的邮箱地址'}  #TODO trans 'invalid login_email'
            self.return_json(400, data=err_msg)
            return False

        #检查指定的role是否存在
        if post_data['role_id'] not in Roles.AVAILABLE_ROLES:
            err_msg = {'detail': u'指定的Role ID 不存在'}  #TODO trans 'given role does not exist'
            self.return_json(400, data=err_msg)
            return False

        self.request_data = post_data
        return True

    def post(self, company_id):
        #TODO 需要邀请注册地址
        if not self._post_check():
            return

        company = Company.objects.filter(Company.id == company_id).filter(Company.state != CompanyState.DELETE).first()

        if not self.check_relation_company(company):
            return

        login_email = self.request_data['login_email']
        role_id = self.request_data['role_id']

        #未成功邀请过的用户都可以继续邀请
        user = User.objects.filter(User.login_email == login_email).first()
        if user is not None:
            err_msg = {'detail': u'邮箱已存在'}  #TODO trans 'email has already registed'
            return self.return_json(403, data=err_msg)

        #未成功邀请过的用户都可以继续邀请
        invite_his = InviteLog.objects.filter(InviteLog.login_email == login_email).filter(
            InviteLog.invite_state != InviteState.EMAILFAILED).first()
        if invite_his is not None:
            err_msg = {'detail': u'已经邀请过的邮箱'}  #TODO trans 'login_email has already been invited'
            return self.return_json(403, data=err_msg)

        invite_log = InviteLog(company_id = company.id, user_id=self._api_user_.id, login_email=login_email,invite_role=role_id)

        flag = send_invite_email(self._api_user_.belong.name, login_email, invite_log.invite_key) #TODO design email style
        invite_state = InviteState.EMAILSUCCESS if flag else InviteState.EMAILFAILED
        invite_log.invite_state=invite_state
        invite_log.save()

        if flag:
            self.return_json(200)
        else:
            err_msg = {'detail': u'发送邀请邮件失败, 请稍后再尝试'}  #TODO trans 'invite user failed , please try later'
            self.return_json(500, data=err_msg)

@auth
class CompanyLogHandler(BaseCompanyHandler):

    def _get_check(self):
        post_data = self.get_request_data()

        start = post_data.get('start',0)
        if start != 0 and (start is None or not start.isdigit()):
            err_msg = {'detail':'start must be integer'}
            self.return_json(400,data=err_msg)
            return False
        post_data['start']=int(start)
        end = post_data.get('end',20)
        if start != 0 and (start is None or not start.isdigit()):
            err_msg = {'detail':'start must be integer'}
            self.return_json(400,data=err_msg)
            return False
        post_data['end']=int(end)
        if post_data['end'] < post_data['start']:
            err_msg = {'detail':'start can not be greater than end'}
            return self.return_json(400,data=err_msg)

        self.request_data = post_data
        return True

    def get(self,company_id):

        if not self._get_check():
            return

        company = Company.objects.filter(Company.id == company_id).filter(Company.state != CompanyState.DELETE).first()

        if not self.check_relation_company(company):
            return

        start = self.request_data['start']
        end = self.request_data['end']
        limit = end-start

        logs = get_access_log_by_company(company.id,start,limit)
        return self.return_json(data=logs)

@auth
class CompanyChannelLogHandler(BaseCompanyHandler):

    def _get_check(self):
        post_data = self.get_request_data()

        # start = post_data.get('start',0)
        # if start != 0 and (start is None or not start.isdigit()):
        #     err_msg = {'detail':'start must be integer'}
        #     self.return_json(400,data=err_msg)
        #     return False
        # post_data['start']=int(start)
        # end = post_data.get('end',20)
        # if start != 0 and (start is None or not start.isdigit()):
        #     err_msg = {'detail':'start must be integer'}
        #     self.return_json(400,data=err_msg)
        #     return False
        # post_data['end']=int(end)
        # if post_data['end'] < post_data['start']:
        #     err_msg = {'detail':'start can not be greater than end'}
        #     return self.return_json(400,data=err_msg)

        self.request_data = post_data
        return True

    def get(self,company_id, channel_id):

        if not self._get_check():
            return

        company = Company.objects.filter(Company.id == company_id).filter(Company.state != CompanyState.DELETE).first()

        if not self.check_relation_company(company):
            return

        # start = self.request_data['start']
        # end = self.request_data['end']
        # limit = end-start

        logs = get_access_log_by_channel_no_page(company.id,channel_id)
        return self.return_json(data=logs)

@auth
class PnListHandler(BaseHandler):

    def get(self):
        request_data = self.get_request_data()
        pn = request_data.get('pn',None)

        result = []
        force = 'f' in request_data
        product_ins_list = ProductIns.objects.all()
        for pn_ins in product_ins_list:
            pn_json = pn_ins.pn_json(force)
            if pn is not None and pn_json['pn'] == pn:
                return self.return_json(data = pn_json)
            result.append(pn_json)

        return self.return_json(data=result)

@auth
class DomainHandler(BaseHandler):

    def get(self):
        result = []
        product_ins_list = ProductIns.objects.all()
        for pn_ins in product_ins_list:
            result.append(pn_ins.pn_json())

        domain_name = self.get_request_data().get('domain',None)
        if domain_name is None:
            return self.return_json(data=result)

        for pn in result:
            for channel in pn['channels']:
                for domain in channel['domains']:
                    if domain['domain'].lower().find(domain_name.lower())>=0:
                        return self.return_json(data=pn)

        return self.return_json(data={'detail':'nothing found about domain `%s`'%domain_name})