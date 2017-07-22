#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, \
    with_statement

import logging
import time
import config
import traceback
import threading
import cymysql
import collections
from server_pool import ServerPool

class DbTransfer(object):
    instance = None

    def __init__(self):
        self._event = threading.Event()
        self._port_user_table = {}
        self._last_transfer = collections.defaultdict(int)
        self._configs = collections.defaultdict(dict)
        self._mysql_key_table = {
            'user_id': 'userId',
            'node_id': 'nodeId',
            'server_port': 'port',
            'flow_up': 'flowUp',
            'flow_down': 'flowDown',
            'transfer_enable': 'transferEnable',
            'password': 'password',
            'is_locked': 'isLocked',
            'active_at': 'activeAt'
        }
        self._mysql_config = {
            'host': config.MYSQL_HOST,
            'port': config.MYSQL_PORT,
            'user': config.MYSQL_USER,
            'passwd': config.MYSQL_PASS,
            'db': config.MYSQL_DB,
            'charset': 'utf8'
        }

    @staticmethod
    def get_instance():
        if DbTransfer.instance is None:
            DbTransfer.instance = DbTransfer()
        return DbTransfer.instance

    def run(self):
        while True:
            try:
                self.sync_user()
                self.update_transfer()
                self.update_active_time()
            except Exception as e:
                traceback.print_exc()
                logging.warn('db thread except:%s' % e)
            if self._event.wait(config.UPDATE_TIME):
                break

    def stop(self):
        self._event.set()

    def get_format_time(self):
        return time.strftime('%Y-%m-%d %H:%M:%S')

    def get_mysql_keys(self, mysql_alias):
        mysql_keys = []
        for alias in mysql_alias:
            mysql_keys.append(self._mysql_key_table[alias])
        return mysql_keys

    def stop_or_start_server(self, server):
        port = int(server['server_port'])
        password = server['password']
        if hasattr(password, 'encode'):
            password = password.encode('utf-8')

        is_run = ServerPool.get_instance().server_is_run(port)
        is_locked = server['is_locked'] == 'Y'
        out_bound = server['flow_up'] + server['flow_down'] >= server['transfer_enable']
        old_password = self._configs[port].get('password', None)

        if is_run and is_locked:
            logging.info('db stop server at port [%s] reason: disable' % (port))
            ServerPool.get_instance().del_server(port)
        elif is_run and out_bound:
            logging.info('db stop server at port [%s] reason: out bandwidth' % (port))
            ServerPool.get_instance().del_server(port)
        elif is_run and old_password != password:
            logging.info('db stop server at port [%s] reason: password changed' % (port))
            ServerPool.get_instance().del_server(port)
        elif not is_run and not is_locked and not out_bound:
            logging.info('db start server at port [%s] pass [%s]' % (port, password))
            config = {
                'server_port': port,
                'password': password
            }
            self._configs[port] = config
            ServerPool.get_instance().add_server(config)

    def get_diff_transfer(self):
        diff_transfer = {}
        curr_transfer = ServerPool.get_instance().get_servers_transfer()
        for port in curr_transfer:
            diff = curr_transfer[port] - self._last_transfer[port]
            if diff <= 1024:
                continue
            diff_transfer[port] = diff
        self._last_transfer = curr_transfer
        return diff_transfer

    def update_user_transfer(self, diff_transfer, now_time):
        update_head = 'UPDATE user'
        update_up_when = ''
        update_down_when = ''
        update_sub_in = None

        mysql_table = self._mysql_key_table
        for port in diff_transfer.keys():
            user_id = self._port_user_table.get(port, None)
            if not user_id:
                continue

            update_up_when += ' WHEN "%s" THEN %s +  %d' % \
                              (user_id, mysql_table['flow_up'], 0)
            update_down_when += ' WHEN "%s" THEN %s + %d' % \
                                (user_id, mysql_table['flow_down'], diff_transfer[port])
            if update_sub_in is not None:
                update_sub_in += ',"%s"' % user_id
            else:
                update_sub_in = '"%s"' % user_id

        if update_sub_in is None:
            return

        update_sql = '%s SET %s = CASE %s %s END, %s = CASE %s %s END, %s = "%s" WHERE %s IN (%s)' % \
                     (update_head, mysql_table['flow_up'], mysql_table['user_id'], update_up_when,
                     mysql_table['flow_down'], mysql_table['user_id'], update_down_when,
                     mysql_table['active_at'], now_time, mysql_table['user_id'], update_sub_in)
        conn = cymysql.connect(**self._mysql_config)
        with conn as cursor:
            cursor.execute(update_sql)
            conn.commit()
        conn.close()

    def insert_user_transfer_log(self, diff_transfer, now_time):
        mysql_alias = ['node_id', 'user_id', 'flow_up', 'flow_down', 'active_at']
        mysql_keys = self.get_mysql_keys(mysql_alias)
        insert_sql = 'INSERT INTO transfer(%s) ' % (', '.join(mysql_keys)) + \
                     'VALUES (%s, %s, %s, %s, %s)'

        insert_rows = []
        for port in diff_transfer.keys():
            user_id = self._port_user_table.get(port, None)
            if not user_id:
                continue
            insert_rows.append([config.NODE_ID, user_id, 0, diff_transfer[port], now_time])

        if not insert_rows:
            return

        conn = cymysql.connect(**self._mysql_config)
        with conn as cursor:
            cursor.executemany(insert_sql, insert_rows)
            conn.commit()
        cursor.close()

    def sync_user(self):
        mysql_alias = [
            'user_id', 'server_port',
            'flow_up', 'flow_down',
            'transfer_enable',
            'password', 'is_locked'
        ]
        mysql_keys = self.get_mysql_keys(mysql_alias)

        conn = cymysql.connect(**self._mysql_config)
        with conn as cursor:
            sql = 'SELECT ' + ', '.join(mysql_keys) + ' FROM user'
            cursor.execute(sql)

            rows = []
            for r in cursor.fetchall():
                row = {}
                for column in range(len(mysql_alias)):
                    row[mysql_alias[column]] = r[column]
                rows.append(row)

        conn.close()

        for row in rows:
            row['server_port'] = int(row['server_port'])
            self._port_user_table[row['server_port']] = row['user_id']
            self.stop_or_start_server(row)

    def update_transfer(self):
        diff_transfer = self.get_diff_transfer()
        now_time = self.get_format_time()
        self.update_user_transfer(diff_transfer, now_time)
        self.insert_user_transfer_log(diff_transfer, now_time)

    def update_active_time(self):
        conn = cymysql.connect(**self._mysql_config)
        with conn as cursor: 
            active_at = self.get_format_time()
            active_at_key = self._mysql_key_table['active_at']
            node_id_key = self._mysql_key_table['node_id']
            update_sql = 'UPDATE node SET %s = "%s" WHERE %s = %d' % \
                        (active_at_key, active_at, node_id_key, config.NODE_ID)
            cursor.execute(update_sql)
            conn.commit()
        conn.close()