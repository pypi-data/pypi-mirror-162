#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : url_config.py


import enum

class URLConf(enum.Enum):
    '''
    环境配置枚举类
    '''
    INDEX_URL = 'https://www.baidu.com'
    NEWS_URL= 'http://news.baidu.com/'

if __name__ == '__main__':
    print(URLConf.INDEX_URL.name)
    print(URLConf.INDEX_URL.value)