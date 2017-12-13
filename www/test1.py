#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'''
Models for user,blog.comment.
'''
__author__= 'zzj'

import sys
import orm,asyncio
from models import User, Blog, Comment

async def test(loop):
	await orm.create_pool(loop=loop,user='www-data', password='', db='awesome',)
	u=User(name='Test1', email='test1@example.com', passwd='1234567890', image='about:blank')

	await u.save()
	await orm.destory_pool()

loop = asyncio.get_event_loop()
loop.run_until_complete(test(loop))
loop.close()