# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author : Mike Zhou
# @Email : 公众号：测试开发技术


'''
按指定用例名称模糊匹配测试用例
'''

import pytest

# 定义表达式运行含有指定的关键字名称的测试用例
name = "test"
pytest.main(["-v","-s","-k", f"{name}"])