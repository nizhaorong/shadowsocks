#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

# BIND IP
# if you want bind ipv4 and ipv6 '::'
# if you want bind all of ipv4 if '0.0.0.0'
#if you want bind all of if only '4.4.4.4'
SERVER = '0.0.0.0'
METHOD = 'rc4-md5'
TIMEOUT = 60
FAST_OPEN = False

# mysql config
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3306
MYSQL_USER = 'root'
MYSQL_PASS = 'root'
MYSQL_DB = 'shadowsocks'

NODE_ID = 1
UPDATE_TIME = 60

# LOG CONFIG
LOG_ENABLE = True
LOG_LEVEL = logging.INFO
LOG_FILE = '/tmp/shadowsocks.log'