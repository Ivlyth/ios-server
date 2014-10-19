#!/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : myth
Date   : 14-9-29
Email  : belongmyth at 163.com
'''

#代理商查询

from base import BaseHandler
from models.agent import Agent
from models.product import ProductIns

#jeason 博客互动

class AgentHandler(BaseHandler):

    def get(self):
        self.request_data = self.get_request_data()
        agent_alias = self.request_data.get('agent',None)
        if agent_alias is None:
            return
        agent = Agent.objects.filter(Agent.alias == agent_alias).first()
        if agent is None:
            return
        companys = [ c.company for c in agent.companys ]
        result = []
        for c in companys:
            pns = ProductIns.objects.filter(ProductIns.company_id==c.id).filter(ProductIns.product_id == 2).all()
            if not pns:
                continue
            data = {}
            data['company_name'] = c.name
            data['pns'] = [{'pn':p.id,'type':p.product.desc} for p in pns]
            result.append(data)
        return self.return_json(data = result)