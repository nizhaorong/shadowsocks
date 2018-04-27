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

from __future__ import absolute_import, division, print_function, \
    with_statement

import logging
import requests
import config
import traceback
import threading
import collections
from server_pool import ServerPool

class ServerControl(object):
    instance = None

    def __init__(self):
        self._event = threading.Event()
        self._port_user_table = {}
        self._last_traffic = collections.defaultdict(int)
        self._users = collections.defaultdict(dict)

    @staticmethod
    def get_instance():
        if ServerControl.instance is None:
            ServerControl.instance = ServerControl()
        return ServerControl.instance

    def run(self):
        while True:
            try:
                logging.info('start synchronizing data')
                self.sync_user()
                self.update_traffic()
                logging.info('synchronized data successfully')
            except Exception as e:
                traceback.print_exc()
                logging.warn('synchronous data exception:%s' % e)
            if self._event.wait(config.UPDATE_TIME):
                logging.info('stoping control thread')
                break

    def stop(self):
        self._event.set()

    def do_request(self, endpoint, data = None):
        url = config.API_URL.rstrip('/') + endpoint
        headers = {
            'node-token': config.NODE_TOKEN
        }
        if data is None:
            return requests.get(url, headers = headers).json()
        return requests.post(url, json = data, headers = headers).json()

    def fetch_users(self):
        return self.do_request('/api/nodes/' + str(config.NODE_ID) + '/users')

    def upload_traffic(self, data):
        return self.do_request('/api/nodes/' + str(config.NODE_ID) + '/traffic', data)

    def stop_or_start_server(self, user):
        port = int(user['port'])
        if hasattr(user['password'], 'encode'):
            user['password'] = user['password'].encode('utf-8')
        password = user['password']

        is_run = ServerPool.get_instance().server_is_run(port)
        old_password = self._users[port].get('password', None)


        if is_run and user['isLocked']:
            logging.info('stop server at port [%s] reason: disable' % (port))
            ServerPool.get_instance().del_server(port)
        elif is_run and old_password != password:
            logging.info('stop server at port [%s] reason: password changed' % (port))
            ServerPool.get_instance().del_server(port)
        elif not is_run:
            logging.info('start server at port [%s] pass [%s]' % (port, password))
            ServerPool.get_instance().add_server({
                'server_port': port,
                'password': password
            })
            self._users[port] = user

    def sync_user(self):
        users = self.fetch_users()
        for user in users:
            self.stop_or_start_server(user)

    def update_traffic(self):
        data = []
        servers_traffic = ServerPool.get_instance().get_servers_traffic()
        for port in servers_traffic:
            userId = self._users[port].get('userId', None)
            if userId is None:
                continue
            diff = servers_traffic[port] - self._last_traffic[port]
            data.append({
                'userId': userId,
                'flowUp': 0,
                'flowDown': diff,
            })
        self._last_traffic = servers_traffic
        self.upload_traffic(data)