shadowsocks for ss-panel
===========

## 部署

### 使用 Docker + Docker Compose 部署

- 配置 docker-compose.yml

```bash
cat > ./docker-compose.yml << \EOF
version: '3'
services:
  python:
    image: qious/shadowsocks:python
    restart: always
    network_mode: host
    environment:
      APP_SREVER: '::'
      APP_METHOD: aes-256-cfb
      APP_TIMEOUT: 60
      APP_FAST_OPEN: 'false'
      APP_LOG_ENABLE: 'true'
      APP_LOG_LEVEL: info
      APP_API_URL: https://example.com/
      APP_NODE_ID: 1
      APP_NODE_TOKEN: token
      APP_UPDATE_TIME: 30
EOF
```

- 运行

```bash
docker-compose up -d
```

### 环境变量说明

| 字段   | 描述   |
|:----|:----|
| APP_SREVER   | shadowsocks 的 server 字段，docker 请使用 '::' 或者 '0.0.0.0'   |
| APP_METHOD   | shadowsocks 的加密方式   |
| APP_TIMEOUT   | shadowsocks 的超时时间   |
| APP_FAST_OPEN   | shadowsocks 的 TCP Fast Open   |
| APP_LOG_ENABLE   | 是否打印日志，建议设置为 true   |
| APP_LOG_LEVEL   | 日志打印等级   |
| APP_API_URL   | ss-panel 对应的地址   |
| APP_NODE_ID   | ss-panel 对应的节点编号   |
| APP_NODE_TOKEN   | ss-panel 对应的节点Token   |
| APP_UPDATE_TIME   | shadowsocks 与 ss-panel 的交互时间间隔   |

shadowsocks
===========

[![PyPI version]][PyPI]
[![Build Status]][Travis CI]
[![Coverage Status]][Coverage]

A fast tunnel proxy that helps you bypass firewalls.

Features:
- TCP & UDP support
- User management API
- TCP Fast Open
- Workers and graceful restart
- Destination IP blacklist

Server
------

### Install

Debian / Ubuntu:

    apt-get install python-pip
    pip install shadowsocks

CentOS:

    yum install python-setuptools && easy_install pip
    pip install shadowsocks

Windows:

See [Install Shadowsocks Server on Windows](https://github.com/shadowsocks/shadowsocks/wiki/Install-Shadowsocks-Server-on-Windows).

### Usage

    ssserver -p 443 -k password -m aes-256-cfb

To run in the background:

    sudo ssserver -p 443 -k password -m aes-256-cfb --user nobody -d start

To stop:

    sudo ssserver -d stop

To check the log:

    sudo less /var/log/shadowsocks.log

Check all the options via `-h`. You can also use a [Configuration] file
instead.

### Usage with Config File

[Create configeration file and run](https://github.com/shadowsocks/shadowsocks/wiki/Configuration-via-Config-File)

To start:

    ssserver -c /etc/shadowsocks.json


Documentation
-------------

You can find all the documentation in the [Wiki](https://github.com/shadowsocks/shadowsocks/wiki).

License
-------

Apache License







[Build Status]:      https://img.shields.io/travis/shadowsocks/shadowsocks/master.svg?style=flat
[Coverage Status]:   https://jenkins.shadowvpn.org/result/shadowsocks
[Coverage]:          https://jenkins.shadowvpn.org/job/Shadowsocks/ws/PYENV/py34/label/linux/htmlcov/index.html
[PyPI]:              https://pypi.python.org/pypi/shadowsocks
[PyPI version]:      https://img.shields.io/pypi/v/shadowsocks.svg?style=flat
[Travis CI]:         https://travis-ci.org/shadowsocks/shadowsocks

