#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, \
    with_statement

import time
import logging
import threading
import config
import traceback
from server_pool import ServerPool
from db_transfer import DbTransfer

if config.LOG_ENABLE:
    datefmt = '%Y, %b %d %a %H:%M:%S'
    logformat = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    logging.basicConfig(format=logformat, datefmt=datefmt, filename=config.LOG_FILE, level=config.LOG_LEVEL)

class ServerPoolThread(threading.Thread):
    def __init__(self, ss_config):
        super(ServerPoolThread, self).__init__()
        self.config = ss_config

    def run(self):
        ServerPool.get_instance().set_config(self.config)
        ServerPool.get_instance().run()

    def stop(self):
        ServerPool.get_instance().stop()

class DbTransferThread(threading.Thread):
    def __init__(self):
        super(DbTransferThread, self).__init__()

    def run(self):
        DbTransfer.get_instance().run()

    def stop(self):
        DbTransfer.get_instance().stop()

def main():
    ss_config = {
        'server': config.SERVER,
        'local_port': 1088,
        'port_password': {},
        'method': config.METHOD,
        'timeout': config.TIMEOUT,
        'fast_open': config.FAST_OPEN,
        'crypto_path': dict(),
        'verbose': 1
    }
    server_pool_thread = ServerPoolThread(ss_config)
    server_pool_thread.start()
    db_transfer_thread = DbTransferThread()
    db_transfer_thread.start()

    try:
        while True:
            time.sleep(100)
    except KeyboardInterrupt as e:
        traceback.print_exc()
        server_pool_thread.stop()
        db_transfer_thread.stop()

if __name__ == '__main__':
    main()