#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-7-14
Email  : belongmyth at 163.com
'''

import json
import types
import httplib
import urllib

import tornado.web
import tornado.gen
import tornado.httpclient
from tornado.escape import json_encode


class BaseHandler(tornado.web.RequestHandler):
    def initisalize(self, **kwargs):
        """
        初始化被__init__调用
        接受来自url_patterns中，第三个字典参数作为参数
        """
        pass

    def prepare(self):
        """
        该方法不能接受其他参数，否则报错
        用于数据库连接初始化等操作
        """
        pass

    @property
    def mysql_session(self):
        return self.application.mysql_session

    @property
    def boss_mysql_session(self):
        return self.application.boss_mysql_session

    @property
    def watermelon_mysql_session(self):
        return self.application.watermelon_mysql_session

    @property
    def redis_session(self):
        return self.application.redis_session

    @property
    def logger(self):
        return self.application.logger

    def get(self, *args, **kwargs):
        self.set_status(405, 'Method Not Allowed')

    def post(self, *args, **kwargs):
        self.set_status(405, 'Method Not Allowed')

    def put(self, *args, **kwargs):
        self.set_status(405, 'Method Not Allowed')

    def delete(self, *args, **kwargs):
        self.set_status(405, 'Method Not Allowed')

    def patch(self, *args, **kwargs):
        self.set_status(405, 'Method Not Allowed')

    def options(self, *args, **kwargs):
        """
        处理CORS Preflighted request
        默认由set_default_headers完成
        """
        pass

    def on_finish(self):
        """
        RequestHandler最后执行的方法，被finish()调用
        释放资源等操作在这里完成
        """
        self.mysql_session.close()
        self.boss_mysql_session.close()
        self.watermelon_mysql_session.close()

    def get_current_user(self):
        """
        配合authenticated装饰器
        前端对于没有登录的用户会重定向到配置文件中的login_url
        用于用户认证，返回 自定义的 user object
        """
        authtoken = self.request.headers.get('Authorization', '')
        if not authtoken: return None
        res = self.redis_session.hget('Hash:LoginAuth', authtoken)  # login handler save user to redis by hset method.
        self.current_user = res
        return self.current_user

    def return_json(self, status_code=200, reason=None, data={}):
        """
        返回json数据，如果有callback则返回jsonp
        """
        assert isinstance(data, (types.BooleanType,
                                 types.NoneType,
                                 types.StringType,
                                 types.DictType,
                                 types.ListType,
                                 types.StringTypes))
        if reason is None:
            reason = httplib.responses.get(status_code)

        callback = self.get_argument('callback', '') or self.get_argument('jsonp', '')
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        self.set_status(status_code, reason)

        if data is not None:
            json_data = json_encode(data)  #json.dumps(data)
            data_p = callback + '(' + json_data + ')' if callback else json_data
            self.write(data_p)

    def set_www_auth_header(self, error='invalid_token', error_desc='the token expired', realm='reserve'):
        """
        验证消息通过WWW-Authenticate头返回
        """
        value = 'Bearer realm="%s", error="%s", error_description="%s"' % (realm, error, error_desc)
        self.set_header('WWW-Authenticate', value)

    def set_cache_headers(self):
        """ 设置缓存头信息 """
        self.set_header('Cache-Control', 'must-revalidate, no-cache, private')
        self.set_header('Pragma', 'no-cache')
        self.set_header('Expires', 'Mon, 26 Jul 1970 05:00:00 GMT')
        self.set_header('Last-Modified', 'Mon, 26 Jul 1970 05:00:00 GMT')

    def set_default_headers(self):
        """
        RequestHandler基类初始化时执行该方法
        设置默认响应header
        post, get, put, delete, patch, options都会执行该方法
        """
        self.set_access_control_header()

    def set_access_control_header(self):
        """
        用于和options方法协商
        跨域Access-Control头信息
        """
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Credentials', 'true')
        self.set_header('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Depth, User-Agent, '
                        'X-File-Size, X-Requested-With, '
                        'X-Requested-By, If-Modified-Since, '
                        'X-File-Name, Cache-Control,'
                        'Authorization, X-Testing, Tan14-Key, '
                        'Accept, Accept-Encoding, Accept-Language, Referer, Host, Origin')

    def get_request_data(self):
        """
        解析请求参数
        返回 dict
        """
        if hasattr(self, 'request_data'):
            return getattr(self, 'request_data')

        data_args = self.parse_request_args()
        data_body = self.parse_request_body()
        # 合并
        res = data_args if data_args.update(data_body) or data_args else data_body

        # ---
        # n_res = {urllib.unquote_plus(key).decode('utf-8'): urllib.unquote_plus(value).decode('utf-8') for key, value in res.iteritems()}
        # print n_res
        # tmp = {}
        # for key, value in res.iteritems():
        #     tmp.setdefault(urllib.unquote_plus(key), urllib.unquote_plus(value))
        # print tmp
        # ---
        setattr(self, 'request_data', res)
        return res

    def parse_request_body(self):
        """ 处理application/json类型的请求 """
        body = {}
        if self.request.body:
            #self.request.body = urllib.unquote(self.request.body)  #unquote params first
            try:
                body = json.loads(self.request.body)
            except ValueError:
                tmp = self.request.body.split('&')
                try:
                    for item in tmp:
                        r = item.split('=')
                        if len(r) != 2:
                            continue
                        k, v = r
                        #body[k.strip()] = v.strip()
                        body[urllib.unquote(k.strip())] = urllib.unquote(v.strip())
                except ValueError:
                    pass
        return body

    def parse_request_args(self):
        """处理请求字符串"""
        args = {}
        if self.request.arguments:
            for key, value in self.request.arguments.iteritems():
                if len(value) == 1:
                    args.setdefault(key, value[0])
                else:
                    args.setdefault(key, value)
        return args


    def write_error_not_use_for_now(self, status_code, **kwargs):
        """
        RequestHandler._execute方法内部依次执行prepare, get/post/delete/put/...，finish
        任何未捕获的错误，都会执行该方法
        覆盖该方法实现自定义错误页面
        """
        self.set_status(status_code, 'Tornado Server Error')
        self.write('Remote server has an inner error, we sorry for this :(')


class PageNotFoundHandler(BaseHandler):
    """处理404页面"""

    def get(self, *args, **kwargs):
        self.set_status(404, 'Page Not Found')

    def post(self, *args, **kwargs):
        self.set_status(404, 'Page Not Found')

    def put(self, *args, **kwargs):
        self.set_status(404, 'Page Not Found')

    def delete(self, *args, **kwargs):
        self.set_status(404, 'Page Not Found')

    def patch(self, *args, **kwargs):
        self.set_status(404, 'Page Not Found')

    def options(self, *args, **kwargs):
        self.set_status(404, 'Page Not Found')


class AsyncExampleHandler(BaseHandler):
    """
    异步调用示例
    以下两种写法等价，gen.Task用于回调中异常处理，否则异常不能被捕获
    try:
        yield http_client.fetch(url)    该方法不能捕获到fetch产生的异常
    except:
        pass

    yield gen.Task(http_client.fetch, url)
    """

    # get方法内部，单个请求
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def single_get(self):
        url = 'www.example.com'
        http_client = tornado.httpclient.AsyncHTTPClient()
        response = yield http_client.fetch(url)
        self.do_response(response)
        self.finish()


    # get方法内部，多个请求
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def multi_get(self):
        urls = ['a.example.com', 'b.example.com', 'c.example.com']
        http_client = tornado.httpclient.AsyncHTTPClient()
        response_list = yield [http_client.fetch(url) for url in urls]  # 返回一个respose列表，每一项为一个url的请求结果
        for response in response_list:
            # 处理response_list
            self.do_response(response)
        self.finish()

    # 异步调用从get方法中分离
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def seperate_get(self):
        urls = ['a.example.com', 'b.example.com', 'c.example.com']
        resp_list = yield [self.async_call(url) for url in urls]
        self.do_response(resp_list)
        self.finish()

    @tornado.gen.coroutine
    def async_call(self, url):
        """
        python2中分离的异步回调必须用raise触发Return异常返回结果
        python3中则使用return
        """
        http_client = tornado.httpclient.AsyncHTTPClient()
        response = yield http_client.fetch(url)
        raise tornado.gen.Return(response)

    def do_response(self, response):
        """
        response对象有两个主要属性 code和body
        code: http响应状态码 200 为正常请求
        body: http响应数据
        """
        if response.code == 200:
            result = response.body
            # do_result
            pass
        else:
            pass
