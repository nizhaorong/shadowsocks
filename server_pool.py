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
import threading
import collections

from shadowsocks import common, eventloop, tcprelay, udprelay, asyncdns

class ServerPool(object):
    instance = None

    def __init__(self):
        self._config = {}
        self._relays = {}
        self._loop = eventloop.EventLoop()
        self._dns_resolver = asyncdns.DNSResolver()
        self._dns_resolver.add_to_loop(self._loop)
        self._statistics = collections.defaultdict(int)

    @staticmethod
    def get_instance():
        if ServerPool.instance is None:
            ServerPool.instance = ServerPool()
        return ServerPool.instance

    def set_config(self, config):
        self._config = config

    def get_config(self):
        return self._config.copy()

    def run(self):
        self._loop.run()

    def stop(self):
        self._loop.stop()

    def server_is_run(self, port):
        return int(port) in self._relays

    def add_server(self, user_config):
        config = self._config.copy()
        config.update(user_config)
        port = int(config['server_port'])
        if port in self._relays:
            logging.error("server already at %s:%d" % (config['server'], port))
            return False

        logging.info("add server at %s:%d" % (config['server'], port))
        t = tcprelay.TCPRelay(config, self._dns_resolver, False,
                              self.stat_callback)
        u = udprelay.UDPRelay(config, self._dns_resolver, False,
                              self.stat_callback)
        t.add_to_loop(self._loop)
        u.add_to_loop(self._loop)
        self._relays[port] = (t, u)
        return True

    def del_server(self, port):
        port = int(port)
        servers = self._relays.get(port, None)
        if not servers:
            logging.error("server not exist at %d" % port)
            return
        logging.info("del server at %d" % port)
        t, u = servers
        t.close(next_tick=False)
        u.close(next_tick=False)
        del self._relays[port]
        del self._statistics[port]

    def stat_callback(self, port, data_len):
        self._statistics[port] += data_len

    def get_servers_traffic(self):
        return self._statistics.copy()