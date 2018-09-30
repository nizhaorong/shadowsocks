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

import os
import logging

# BIND IP
# if you want bind ipv4 and ipv6 '::'
# if you want bind all of ipv4 if '0.0.0.0'
#if you want bind all of if only '4.4.4.4'
SERVER = os.environ.get('APP_SREVER', '::')
METHOD = os.environ.get('APP_METHOD', 'aes-256-cfb')
TIMEOUT = int(os.environ.get('APP_TIMEOUT', '60'))
FAST_OPEN = os.environ.get('APP_FAST_OPEN', 'false').lower() == 'true'

# LOG CONFIG
LOG_ENABLE = os.environ.get('APP_LOG_ENABLE', 'true').lower() == 'true'
LOG_LEVEL = os.environ.get('APP_LOG_LEVEL', 'DEBUG').upper()

# Node Info
API_URL = os.environ.get('APP_API_URL', 'http://example.com/')
NODE_ID = os.environ.get('APP_NODE_ID', '1')
NODE_TOKEN = os.environ.get('APP_NODE_TOKEN', 'token')
SYNC_INTERVAL = int(os.environ.get('APP_SYNC_INTERVAL', '30'))