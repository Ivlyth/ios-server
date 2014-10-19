#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-10-14
Email  : belongmyth at 163.com
'''

from base import BaseHandler
from models.product import ProductIns
from settings import TAN14_KEY

from tornado import gen
from tornado.concurrent import Future

import urllib,urllib2,json

class BlackIPHandler(BaseHandler):
    '''
       根据提供的 domain 和 IP 地址 ,
       来自动添加黑名单 IP 到对应的频道
       并自动完成下发动作
    '''

    def _get_check(self):
        self.request_data = self.get_request_data()
        return True

    def _get_satisfy_domain_list(self):

        domain = self.request_data.get('domain',None)
        ip = self.request_data.get('ip',None)

        if domain is None or ip is None:
            result = u'<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><center>domain 或者 ip 不能为空<br/><a href="/useful/autoblack" blank="_self">返回<a/><center/>'
            self.write(result)
            return

        result = []
        product_ins_list = ProductIns.objects.all()
        for pn_ins in product_ins_list:
            result.append(pn_ins.pn_json())

        domain_name = self.get_request_data().get('domain',None)
        if domain_name is None:
            return self.return_json(data=result)

        domain_info_list = []

        for pn in result:
            for channel in pn['channels']:
                for domain in channel['domains']:
                    if domain['domain'].lower().find(domain_name.lower())>=0:
                        domain_info_list.append({
                            'pn':pn['pn'],
                            'company_name':pn['company'],
                            'company_alias':pn['company_alias'],
                            'channel_remark':channel['remark'],
                            'channel_id':channel['channel_id'],
                            'product_type':pn['product_type'],
                            'domain_name':domain['domain'],
                            'domain_remark':domain['remark'],
                            'website_addr':pn['website'][0]['addr'],
                            'api_prefix':pn['website'][0]['api_prefix'],
                            'ip':ip
                        })

        return domain_info_list

    @gen.coroutine
    def get(self):
        if not self._get_check():
            return

        step = self.request_data.get('step','1')
        step_func = getattr(self,'_step_%s'%step,None)
        if step_func:
            r = yield step_func()

    def _step_1(self):
        form = u'''
        <br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>
        <center>
        <form action='/useful/autoblack' method='get'>
          <table>
            <tr>
              <td>
                <label for='ip'/><span>IP: </span>
              <td/>
              <td>
                <input id='ip' name='ip' type='text' placeholder='黑名单IP,多个用逗号分隔'/>
              <td/>
            <tr/>
            <tr>
              <td>
                <label for='domain'/><span>Domain: </span>
              <td/>
              <td>
                <input id='domain' name='domain' type='text' placeholder='要检索的域名'/>
              <td/>
            <tr/>
            <tr>
              <td>
                <input name='step' type='hidden' value='2'/>
              <td/>
              <td>
                <input type='submit' value='确定'/>
              <td/>
            <tr/>
            <tr>
              <td>
                <a target='_blank' href='https://api.tan14.cn/company/pnlist'>点此查看域名列表<a/>
              <td/>
              <td>
                <a target='_blank' href='https://github.com/callumlocke/json-formatter'>下载JSON Formatter插件<a/>
              <td/>
            <tr/>
        </form>
        <center/>
        '''
        self.write(form)
        future = Future()
        future.set_result(True)
        return future

    def _step_2(self):
        '''
        与 用户交互
        '''
        domain_list = self._get_satisfy_domain_list()
        if len(domain_list) == 0:
            result = u'<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><center>没有找到可以匹配的域名<br/><a href="/useful/autoblack" blank="_self">返回<a/><center/>'
            self.write(result)
            future = Future()
            future.set_result(True)
            return future
        result = u'<table><thead><tr><td>公司名称<td/><td>使用产品<td/><td>频道<td/><td>域名<td/><td>执行<td/><tr/><thead/><tbody>'
        lines = []
        for domain in domain_list:
            tr = u'''<tr><td><a target='_blank' href="https://api.tan14.cn/company/pnlist?pn=%(pn)s" title="登陆别名 - %(company_alias)s \n 点击查看公司详细信息">%(company_name)s<a/><td/>
                 <td><a target='_blank' href="%(website_addr)s/#/login?e=root@tan14.cn.%(company_alias)s&p=fW9?2/Hw" title="点击登录产品" >%(product_type)s<a/><td/>
                 <td><a href="" title="频道ID - %(channel_id)s">%(channel_remark)s<a/><td/>
                 <td><a href="" title="域名remark - %(domain_remark)s">%(domain_name)s<a/><td/>
                 <td><a target='_blank' href="/useful/autoblack?domain=%(domain_name)s&ip=%(ip)s&pn=%(pn)s&channel_id=%(channel_id)s&api_prefix=%(api_prefix)s&step=3">点击添加</a><td/><tr/>'''
            lines.append(tr%domain)
        result += u''.join(lines)
        result += u'<tbody/><table/>'
        result = u'<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><center>'+result+u'<center/><br/><a href="/useful/autoblack" blank="_self">返回<a/>'
        self.write(result)
        future = Future()
        future.set_result(True)
        return future

    def _step_3(self):
        '''
         各种请求
        '''
        url = 'https://api.tan14.cn/%(api_prefix)s/%(pn)s/channel/%(channel_id)s/blackwhite'
        new_url = url%self.request_data
        ip = self.request_data.get('ip',None)
        print 'step3 ip is ',ip
        if ip is None:
            result = u'<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><center>ip 不能为空<br/><a href="/useful/autoblack" blank="_self">返回<a/><center/>'
            self.write(result)
            future = Future()
            future.set_result(False)
            return future

        new_black_ips = ''

        try:
            print 'step3 newurl is ',new_url
            req = urllib2.Request(new_url,headers={'Tan14-Key':TAN14_KEY})
            print 'step3 111111111111 '
            res = urllib2.urlopen(req).read()
            print 'step3 222222222222'
            res = json.loads(res)
            print 'step3 333333333333'
            black_ips = res.get('black_ips','')
            black_ips = black_ips.strip(';')
            new_black_ips = black_ips + ';' + ip.strip(';').strip(',').replace(',',';')
            new_black_ips = new_black_ips.strip().strip(';')
        except Exception as e:
            code = str(e.code)
            print 'step3 err is ',e
            if code == '401':
                self.write('Tan14Key 失效,请联系开发更新')
                future = Future()
                future.set_result(False)
                return future
            msg = e.read()
            try:
                if code == '404' :
                    msg = json.loads(msg)
                    if 'detail' in msg and msg['detail'] == u'黑白名单不存在':
                        new_black_ips = ip.strip(';').strip(',').replace(',',';')
                    else:
                        result = u'<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><center>Error : %s - %s<center/>'%(e,e.read() if hasattr(e,'read') else '')
                        self.write(result)
                        future = Future()
                        future.set_result(False)
                        return future
                else:
                    result = u'<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><center>Error : %s - %s<center/>'%(e,e.read() if hasattr(e,'read') else '')
                    self.write(result)
                    future = Future()
                    future.set_result(False)
                    return future
            except Exception as e:
                result = u'<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><center>Error : %s - %s<center/>'%(e,e.read() if hasattr(e,'read') else '')
                self.write(result)
                future = Future()
                future.set_result(False)
                return future

        try:
            req = urllib2.Request(new_url,data=urllib.urlencode({'black_ips':new_black_ips}),headers={'Tan14-Key':TAN14_KEY})
            print new_url
            req.get_method = lambda :'PUT'
            res = urllib2.urlopen(req).read()
            applied_url = 'https://api.tan14.cn/%(api_prefix)s/%(pn)s/channel/%(channel_id)s/applied'
            req = urllib2.Request(applied_url%self.request_data,data=urllib.urlencode({'makeitbigger':'ok'}),headers={'Tan14-Key':TAN14_KEY})
            req.get_method = lambda :'PUT'
            print applied_url%self.request_data
            res = urllib2.urlopen(req).read()
            result = u'<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><center>添加成功<br/><center/>'
            self.write(result)
            future = Future()
            future.set_result(True)
            return future
        except Exception as e:
            result = u'<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><center>Error : %s - %s<center/>'%(e,e.read() if hasattr(e,'read') else '')
            self.write(result)
            future = Future()
            future.set_result(False)
            return future

        '''
        https://api.tan14.cn/wp/c63859735fc816628c5532/channel/6c97cd93c2aa7ef1645bf9/blackwhite GET
        black_ips: "3.3.3.3;6.6.6.6;9.9.9.99"
        black_referers: null
        channel_id: "6c97cd93c2aa7ef1645bf9"
        white_ips: null

        detail:

        https://api.tan14.cn/wp/c63859735fc816628c5532/channel/6c97cd93c2aa7ef1645bf9/blackwhite PUT
        black_ips: "3.3.3.3;6.6.6.6;9.9.9.99"
        '''
