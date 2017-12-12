#!/usr/bin/env python3
# -*- coding: utf-8 -*-


'''
Models for user,blog.comment.
'''
__author__= 'zzj'

import time,uuid

from orm import Model, StringField, BooleanField, FloatField, TextField

def next_id():
	return '%015d%s000' % (int(time.time()*1000), uuid.uuid4().hex)

class User(Model):
	"""docstring for User"""
	__table__='users'

	id=
	def __init__(self, arg):
		super(User, self).__init__()
		self.arg = arg
		