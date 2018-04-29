#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2017-2018 qiujun
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

# BIND IP
# if you want bind ipv4 and ipv6 '::'
# if you want bind all of ipv4 if '0.0.0.0'
#if you want bind all of if only '4.4.4.4'
SERVER = '0.0.0.0'
METHOD = 'rc4-md5'
TIMEOUT = 60
FAST_OPEN = False

# Node Info
API_URL = 'http://example.com/'
NODE_ID = 1
NODE_TOKEN = 'token'
UPDATE_TIME = 60

# LOG CONFIG
LOG_ENABLE = True
LOG_LEVEL = logging.INFO
LOG_FILE = '/tmp/shadowsocks.log'