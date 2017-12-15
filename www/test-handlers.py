#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'zzj'

import asyncio
from coroweb import get, post


@get('/')
async def handler_url_blog(request):
    body = '<h1>awesome</h1>'
    return body


@get('/greeting')
async def handler_url_greeting(*, name, request):
    body = '<h1>awesome: /greeting %s</h1>' % name
    return body
