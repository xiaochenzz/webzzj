#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'zzj'

import asyncio
import re
import time
import json
import logging
import hashlib
import base64
import markdown2

from aiohttp import web

from coroweb import get, post
from apis import APIValueError, APIResourceNotFoundError

from models import User, Comment, Blog, next_id
from config import configs


'''
@get('/')
async def handler_url_blog(request):
    body = '<h1>李莎莎是个小猪</h1>'
    return body

@get('/greeting')
async def handler_url_greeting(*, name, request):
    body = '<h1>awesome: /greeting %s</h1>' % name
    return body

@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }
'''


COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret


def user2cookie(user, max_age):
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


async def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/')
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed to eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary,
             created_at=time.time()-120),
        Blog(id='2', name='Something New',
             summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary,
             created_at=time.time()-7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs,
        '__user__': request.__user__
    }


@get('/register')
def register():
    return {
        '__template__': 'register.html'
    }


@get('/signin')
def signin():
    return {
        '__template__': 'signin.html'
    }


@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'invalid email')
    if not passwd:
        raise APIValueError('passwd', 'invalid passwd')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'email not exist.')
    user = users[0]
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', 'invalid password.')
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-daleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

@post('/api/users')
async def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


'''
@get('/api/users')
async def api_get_users():
    users = await User.findAll(orderBy='created_at desc')
    for u in users:
         u.passwd = '******'
    return dict(users=users)
'''