# !/usr/bin/env python
# -*- coding:utf8 -*-
'''
Author : Myth
Date   : 14-10-15
Email  : belongmyth at 163.com
'''
from datetime import datetime

from sqlalchemy import Column, VARCHAR,DATETIME, ForeignKey,INTEGER
from sqlalchemy.orm import relationship, backref


from base import BaseModel,init_db

class Node(BaseModel):

    __tablename__ = 'mc_testnode'

    id = Column('id',INTEGER,primary_key=True)
    name = Column('name',VARCHAR(40))
    desc = Column('desc',VARCHAR(40))
    created = Column('created',DATETIME,default=datetime.now)
    parent_id = Column(ForeignKey('mc_testnode.id'),nullable=True)

    parent = relationship('Node',remote_side=[id],backref = backref('children'))

    def save(self, commit = True):
        self.session.add(self)
        if commit:
            self.session.commit()

    def json(self):
        data = {
            'id':self.id,
            'name':self.name,
            'desc':self.desc,
            'created':self.created.strftime('%Y-%m-%d'),
            'children':[c.json() for c in self.children]
        }
        return data

    @classmethod
    def update(cls,NodeList = []):
        nodes = cls.objects.all()

        nodes_map = {}
        for n in nodes:
            nodes_map[n.id] = n

        if not NodeList:
            return

        def f(parent ,children ):
            for child in children:
                if 'id' in child:
                    # exist node
                    nodes_map[root['id']].parent_id = parent.id
                    new_child = nodes_map[root['id']]
                    new_child.parent_id = parent.id
                else:
                    new_child = Node()
                    new_child.name = child.get('name',None)
                    new_child.desc = child.get('desc',None)
                    new_child.save()
                    new_child.parent_id = parent.id
                    nodes_map[new_child.id] = new_child
                f(new_child, child.get('children',[]))

        for root in NodeList:
            if 'id' in root:
                # exist node
                nodes_map[root['id']].parent_id = None
                #nodes_map[root['id']].save()
                new_root = nodes_map[root['id']]
            else:
                # create new node
                new_root = Node()
                new_root.name = root.get('name',None)
                new_root.desc = root.get('desc',None)
                new_root.save()
                new_root.parent_id = None
                nodes_map[new_root.id] = new_root
            f(new_root, root.get('children',[]))

        cls.session.commit()

if __name__ == '__main__':
    init_db()